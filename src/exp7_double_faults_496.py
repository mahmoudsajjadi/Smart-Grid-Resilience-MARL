import numpy as np
import json
import itertools
import copy
import time
import networkx as nx
import pandapower as pp
import pandapower.networks as pn
import sys

# Load base network
base_net = pn.case33bw()
TIE_LINES = [32, 33, 34, 35, 36]
NORMAL_LINES = list(range(32))

loads = np.zeros(len(base_net.bus))
for _, row in base_net.load.iterrows():
    loads[int(row.bus)] += row.p_mw
TOTAL_LOAD = loads.sum()

ZONE_OF_BUS = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1, 8: 2, 9: 2, 10: 2,
    11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 1, 19: 1,
    20: 1, 21: 1, 22: 3, 23: 3, 24: 3, 25: 4, 26: 4, 27: 4, 28: 4,
    29: 4, 30: 4, 31: 4, 32: 4,
}

tie_geometry = {int(i): (int(base_net.line.at[i, 'from_bus']), int(base_net.line.at[i, 'to_bus']))
                for i in TIE_LINES}

def energized_buses(net):
    G = nx.Graph()
    G.add_nodes_from(net.bus.index)
    for _, row in net.line.iterrows():
        if row.in_service:
            G.add_edge(int(row.from_bus), int(row.to_bus))
    for _, row in net.switch.iterrows():
        if row.closed and row.et == 'b':
            G.add_edge(int(row.bus), int(row.element))
    slack_bus = int(net.ext_grid.bus.iloc[0])
    if slack_bus not in G:
        return set()
    return set(nx.node_connected_component(G, slack_bus))

def is_radial(net):
    G = nx.Graph()
    G.add_nodes_from(net.bus.index)
    for _, row in net.line.iterrows():
        if row.in_service:
            e = (int(row.from_bus), int(row.to_bus))
            if G.has_edge(*e):
                return False
            G.add_edge(*e)
    for comp in nx.connected_components(G):
        sub = G.subgraph(comp)
        if sub.number_of_edges() > sub.number_of_nodes() - 1:
            return False
    return True

def try_double_restoration(base_net, faults, tie_actions):
    net = copy.deepcopy(base_net)
    for f in faults:
        net.line.at[f, 'in_service'] = False
    for t in tie_actions:
        net.line.at[t, 'in_service'] = True

    if not is_radial(net):
        return False, 0.0

    try:
        pp.runpp(net, enforce_q_lims=True, numba=True)
    except Exception:
        return False, 0.0

    if not net['converged']:
        return False, 0.0

    vmin, vmax = net.res_bus.vm_pu.min(), net.res_bus.vm_pu.max()
    max_loading = net.res_line.loading_percent.max() if len(net.res_line) else 0.0
    energized = energized_buses(net)
    restored = sum(loads[b] for b in energized)
    feasible = (vmin >= 0.90) and (vmax <= 1.10) and (max_loading <= 100.0)
    return feasible, restored

def isolated_load(base_net, faults):
    net = copy.deepcopy(base_net)
    for f in faults:
        net.line.at[f, 'in_service'] = False
    en = energized_buses(net)
    all_b = set(net.bus.index)
    iso_b = all_b - en
    return sum(loads[b] for b in iso_b), iso_b

all_pairs = list(itertools.combinations(NORMAL_LINES, 2))
print(f"Total pairs to evaluate: {len(all_pairs)}")

# All 32 subsets of tie switches
all_tie_subsets = []
for r in range(len(TIE_LINES) + 1):
    all_tie_subsets.extend(list(itertools.combinations(TIE_LINES, r)))

results = []
t0 = time.time()
for idx, (f1, f2) in enumerate(all_pairs):
    iso_mw, iso_b = isolated_load(base_net, (f1, f2))
    if iso_mw < 1e-4:
        # No load isolated
        continue
    
    # 1. Centralized exhaustive search
    cen_best = 0.0
    cen_tries = 32
    for sub in all_tie_subsets:
        feas, rest = try_double_restoration(base_net, (f1, f2), sub)
        if feas:
            cen_best = max(cen_best, rest)
    
    # Restored isolated load: rest - (TOTAL_LOAD - iso_mw)
    base_connected = TOTAL_LOAD - iso_mw
    cen_rest_iso = max(0.0, cen_best - base_connected)
    cen_pct = (cen_rest_iso / iso_mw) * 100.0 if iso_mw > 0 else 100.0

    # 2. Decentralized local-first search
    # Zones containing isolated buses
    affected_zones = sorted(list({ZONE_OF_BUS[b] for b in iso_b}))
    claimed_ties = set()
    dec_tries = 1 # baseline check
    
    # Baseline
    feas0, rest0 = try_double_restoration(base_net, (f1, f2), [])
    dec_best = rest0 if feas0 else 0.0
    dec_action = []

    # Round 1: Each affected zone tries its local ties
    for z in affected_zones:
        # local ties for zone z
        z_ties = [t for t, (fb, tb) in tie_geometry.items() if (ZONE_OF_BUS[fb] == z or ZONE_OF_BUS[tb] == z) and t not in claimed_ties]
        for t in z_ties:
            dec_tries += 1
            cand = dec_action + [t]
            feas, rest = try_double_restoration(base_net, (f1, f2), cand)
            if feas and rest > dec_best:
                dec_best = rest
                dec_action.append(t)
                claimed_ties.add(t)

    # Round 2: Escalation if still unserved load
    if (dec_best - base_connected) < iso_mw - 1e-4:
        # Try remaining ties from other zones
        remaining_ties = [t for t in TIE_LINES if t not in claimed_ties]
        for t in remaining_ties:
            dec_tries += 1
            cand = dec_action + [t]
            feas, rest = try_double_restoration(base_net, (f1, f2), cand)
            if feas and rest > dec_best:
                dec_best = rest
                dec_action.append(t)
                claimed_ties.add(t)

    dec_rest_iso = max(0.0, dec_best - base_connected)
    dec_pct = (dec_rest_iso / iso_mw) * 100.0 if iso_mw > 0 else 100.0

    results.append({
        "pair": (f1, f2),
        "iso_mw": iso_mw,
        "cen_pct": cen_pct,
        "dec_pct": dec_pct,
        "cen_tries": cen_tries,
        "dec_tries": dec_tries,
        "gap": cen_pct - dec_pct
    })

    if (idx + 1) % 50 == 0:
        elapsed = time.time() - t0
        print(f"Processed {idx+1}/{len(all_pairs)} pairs ({elapsed:.1f}s)... Mean Cen: {np.mean([r['cen_pct'] for r in results]):.2f}%, Dec: {np.mean([r['dec_pct'] for r in results]):.2f}%")

cen_all = [r["cen_pct"] for r in results]
dec_all = [r["dec_pct"] for r in results]
cen_tr = [r["cen_tries"] for r in results]
dec_tr = [r["dec_tries"] for r in results]
gaps = [r["gap"] for r in results]

n = len(results)
cen_mean, cen_sem = np.mean(cen_all), np.std(cen_all) / np.sqrt(n)
dec_mean, dec_sem = np.mean(dec_all), np.std(dec_all) / np.sqrt(n)
eval_red = (1.0 - np.mean(dec_tr) / np.mean(cen_tr)) * 100.0

print("\n=== FINAL RESULTS ACROSS ALL 496 PAIRS ===")
print(f"Evaluated non-trivial pairs: {n}")
print(f"Centralized (exhaustive): {cen_mean:.2f} +/- {cen_sem:.2f}% (Avg evaluations: {np.mean(cen_tr):.1f})")
print(f"Decentralized (protocol):   {dec_mean:.2f} +/- {dec_sem:.2f}% (Avg evaluations: {np.mean(dec_tr):.1f})")
print(f"Optimality Gap:             {np.mean(gaps):.2f}%")
print(f"Evaluation Reduction:       {eval_red:.1f}%")

with open("all_496_double_faults.json", "w") as f:
    json.dump({
        "n_pairs": n,
        "cen_mean": cen_mean,
        "cen_sem": cen_sem,
        "dec_mean": dec_mean,
        "dec_sem": dec_sem,
        "gap": np.mean(gaps),
        "cen_avg_tries": float(np.mean(cen_tr)),
        "dec_avg_tries": float(np.mean(dec_tr)),
        "eval_reduction_pct": eval_red
    }, f, indent=2)
