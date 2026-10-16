"""
Experiment 5b: Scaling sweep and ablation for restoration search.

Part A  - Per-AC-power-flow cost vs. network size (tie count not involved).
Part B  - Measured restoration search on IEEE 33-bus with T = 5..12 tie
          switches (5 standard + synthetic normally-open ties). Compares:
            (1) naive exhaustive centralized search: AC power flow for all 2^T subsets
            (2) radiality-pruned centralized search: cheap graph check first,
                AC power flow only for radial subsets
            (3) decentralized bounded local search: <= 3 local candidates
          for single faults (all 32 lines) and 20 sampled double faults.
Outputs: data/exp5b_results.json, figures/fig_exp5b_scaling.pdf
"""
import copy, itertools, json, os, random, time, warnings
import numpy as np
import networkx as nx
import pandapower as pp
import pandapower.networks as pn
warnings.filterwarnings("ignore")

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
rng = random.Random(42)

# ---------------- Part A: per-power-flow cost ----------------
def time_pf(net, reps):
    pp.runpp(net)  # warm-up
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); pp.runpp(net); ts.append(time.perf_counter() - t0)
    return float(np.mean(ts)), float(np.std(ts))

partA = {}
for name, fn, reps in [("IEEE 33", pn.case33bw, 30), ("Oberrhein 179", pn.mv_oberrhein, 30),
                       ("IEEE 118", pn.case118, 20), ("IEEE 300", pn.case300, 20),
                       ("PEGASE 1354", pn.case1354pegase, 10), ("PEGASE 2869", pn.case2869pegase, 5)]:
    try:
        net = fn(); m, s = time_pf(net, reps)
        partA[name] = {"buses": len(net.bus), "pf_ms": m * 1e3, "pf_std_ms": s * 1e3}
        print(f"[A] {name}: {len(net.bus)} buses, {m*1e3:.1f} +/- {s*1e3:.1f} ms")
    except Exception as e:
        print(f"[A] {name} failed: {e}")

# ---------------- Part B: measured search on 33-bus ----------------
base = pn.case33bw()
NORMAL = list(range(32)); STD_TIES = [32, 33, 34, 35, 36]
loads = np.zeros(len(base.bus))
for _, r in base.load.iterrows(): loads[int(r.bus)] += r.p_mw
TOTAL = loads.sum()

def add_synthetic_ties(net, k):
    existing = {(int(a), int(b)) for a, b in zip(net.line.from_bus, net.line.to_bus)}
    existing |= {(b, a) for a, b in existing}
    G = nx.Graph(); G.add_edges_from((int(a), int(b)) for a, b in zip(net.line.from_bus[:32], net.line.to_bus[:32]))
    ids = []
    while len(ids) < k:
        a, b = rng.sample(range(1, 33), 2)
        if (a, b) in existing or nx.shortest_path_length(G, a, b) < 4: continue
        r = net.line.loc[35]
        idx = pp.create_line_from_parameters(net, a, b, 1.0, r.r_ohm_per_km, r.x_ohm_per_km,
                                             r.c_nf_per_km, r.max_i_ka, in_service=False)
        existing |= {(a, b), (b, a)}; ids.append(idx)
    return ids

def graph(net):
    G = nx.Graph(); G.add_nodes_from(net.bus.index)
    for i, r in net.line.iterrows():
        if r.in_service:
            if G.has_edge(int(r.from_bus), int(r.to_bus)): return None
            G.add_edge(int(r.from_bus), int(r.to_bus))
    return G

def radial(net):
    G = graph(net)
    return G is not None and nx.is_forest(G)

def evaluate(net, faults, ties, check_radial):
    n = copy.deepcopy(net)
    for f in faults: n.line.at[f, "in_service"] = False
    for t in ties: n.line.at[t, "in_service"] = True
    if check_radial and not radial(n): return False, 0.0, 0
    try: pp.runpp(n)
    except Exception: return False, 0.0, 1
    if not n.converged: return False, 0.0, 1
    ok = n.res_bus.vm_pu.min() >= 0.90 and n.res_bus.vm_pu.max() <= 1.10 \
         and n.res_line.loading_percent.max() <= 100 and radial(n)
    G = graph(n); en = nx.node_connected_component(G, int(n.ext_grid.bus.iloc[0]))
    return ok, float(sum(loads[b] for b in en)) if ok else 0.0, 1

def dead_buses(net, faults):
    n = copy.deepcopy(net)
    for f in faults: n.line.at[f, "in_service"] = False
    G = graph(n); return set(n.bus.index) - nx.node_connected_component(G, int(n.ext_grid.bus.iloc[0]))

def centralized(net, faults, ties, prune, max_size=None):
    best, pf, t0 = 0.0, 0, time.perf_counter()
    for k in range(0, len(ties) + 1):
        if max_size is not None and k > max_size: break
        for sub in itertools.combinations(ties, k):
            ok, served, c = evaluate(net, faults, sub, check_radial=prune); pf += c
            if ok: best = max(best, served)
    return best, pf, time.perf_counter() - t0

def decentralized(net, faults, ties):
    dead = dead_buses(net, faults)
    local = [t for t in ties if int(net.line.at[t, "from_bus"]) in dead or int(net.line.at[t, "to_bus"]) in dead]
    cands = [()] + [(t,) for t in local[:2]]           # <= 3 candidates, as in the paper
    if len(faults) == 2 and len(local) >= 2: cands = [()] + [(t,) for t in local[:1]] + [tuple(local[:2])]
    best, pf, t0 = 0.0, 0, time.perf_counter()
    for c in cands:
        ok, served, n = evaluate(net, faults, c, check_radial=True); pf += n
        if ok: best = max(best, served)
    return best, pf, time.perf_counter() - t0

singles = [(f,) for f in NORMAL]
doubles = rng.sample(list(itertools.combinations(NORMAL, 2)), 20)
partB = {}
for T in [5, 6, 8, 10, 12]:
    net = copy.deepcopy(base); ties = STD_TIES + add_synthetic_ties(net, T - 5)
    res = {}
    for label, cases in [("single", singles), ("double", doubles)]:
        naive_ms = []; pr = {"pf": [], "ms": [], "rest": []}; de = {"pf": [], "ms": [], "rest": []}
        for faults in cases:
            iso = len(dead_buses(net, faults)) and sum(loads[b] for b in dead_buses(net, faults))
            b, p, t = centralized(net, faults, ties, prune=True, max_size=len(faults))
            pr["pf"].append(p); pr["ms"].append(t * 1e3); pr["rest"].append(b)
            b, p, t = decentralized(net, faults, ties)
            de["pf"].append(p); de["ms"].append(t * 1e3); de["rest"].append(b)
        # naive exhaustive: measured on 3 cases only when 2^T <= 1024, else extrapolated
        pf_ms = partA["IEEE 33"]["pf_ms"]
        if 2 ** T <= 256:
            for faults in cases[:3]:
                _, _, t = centralized(net, faults, ties, prune=False); naive_ms.append(t * 1e3)
            naive = float(np.mean(naive_ms)); naive_src = "measured"
        else:
            naive = 2 ** T * pf_ms; naive_src = "extrapolated"
        gap = 100 * (np.mean(pr["rest"]) - np.mean(de["rest"])) / TOTAL
        res[label] = {"T": T, "naive_candidates": 2 ** T, "naive_ms": naive, "naive_src": naive_src,
                      "pruned_pf_calls": float(np.mean(pr["pf"])), "pruned_ms": float(np.mean(pr["ms"])),
                      "dec_pf_calls": float(np.mean(de["pf"])), "dec_ms": float(np.mean(de["ms"])),
                      "pruned_served_pct": 100 * float(np.mean(pr["rest"])) / TOTAL,
                      "dec_served_pct": 100 * float(np.mean(de["rest"])) / TOTAL, "gap_pp": float(gap)}
        r = res[label]
        print(f"[B] T={T:2d} {label:6s}: naive 2^T={2**T:5d} ({naive:8.0f} ms, {naive_src}) | "
              f"pruned PF={r['pruned_pf_calls']:5.1f} ({r['pruned_ms']:6.0f} ms) | "
              f"dec PF={r['dec_pf_calls']:3.1f} ({r['dec_ms']:5.0f} ms) | gap={gap:4.2f} pp")
    partB[T] = res

json.dump({"partA": partA, "partB": partB}, open(os.path.join(OUT, "data", "exp5b_results.json"), "w"), indent=2)

# ---------------- Figure ----------------
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
Ts = sorted(partB)
for lab, ls in [("single", "-"), ("double", "--")]:
    ax[0].semilogy(Ts, [partB[T][lab]["naive_ms"] for T in Ts], "r" + ls, marker="o", label=f"Naive exhaustive ({lab})")
    ax[0].semilogy(Ts, [partB[T][lab]["pruned_ms"] for T in Ts], "b" + ls, marker="s", label=f"Radiality-pruned ({lab})")
    ax[0].semilogy(Ts, [partB[T][lab]["dec_ms"] for T in Ts], "g" + ls, marker="^", label=f"Decentralized ({lab})")
ax[0].axhline(500, color="k", lw=0.8, ls=":"); ax[0].set_xlabel("Tie switches T"); ax[0].set_ylabel("Search time (ms)")
ax[0].set_title("(a) IEEE 33-bus, measured"); ax[0].legend(fontsize=7)
for lab, c in [("single", "C0"), ("double", "C1")]:
    ax[1].plot(Ts, [partB[T][lab]["gap_pp"] for T in Ts], marker="o", color=c, label=lab)
ax[1].set_xlabel("Tie switches T"); ax[1].set_ylabel("Optimality gap (pp of total load)"); ax[1].set_title("(b) Decentralized vs pruned optimum"); ax[1].legend()
names = list(partA); ax[2].loglog([partA[n]["buses"] for n in names], [partA[n]["pf_ms"] for n in names], "ko-")
for n in names: ax[2].annotate(n, (partA[n]["buses"], partA[n]["pf_ms"]), fontsize=7)
ax[2].set_xlabel("Buses"); ax[2].set_ylabel("One AC power flow (ms)"); ax[2].set_title("(c) Per-solve cost vs size")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "figures", "fig_exp5b_scaling.pdf")); plt.savefig(os.path.join(OUT, "figures", "fig_exp5b_scaling.png"), dpi=150)
print("done")
