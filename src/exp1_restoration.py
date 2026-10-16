"""
Experiment 1: N-1 Contingency Resilience -- Centralized vs. Decentralized
Multi-Agent Restoration on the IEEE 33-bus feeder (Baran & Wu, 1989).

For every one of the 32 sectionalizing lines, we simulate its outage and
compare two restoration strategies:
  (a) Centralized: a single controller with full network visibility
      searches all 2^5 = 32 combinations of the 5 tie-switches and adopts
      the feasible combination that restores the most load.
  (b) Decentralized multi-agent: each of the 5 zone agents only knows
      about its own local tie-switch(es); the agent whose zone contains
      the de-energized buses proposes closing its own tie-switch(es)
      first, escalating to a one-hop neighbor-agent request only if its
      own action is infeasible or insufficient. This models a realistic
      limited-communication self-healing protocol.
Feasibility is checked with a full AC power flow (pandapower) requiring
radiality, voltage in [0.90, 1.10] p.u., and line loading <= 100%.
"""
import numpy as np
import json
import itertools
import warnings
warnings.filterwarnings('ignore')
from grid_env import build_base_net, try_restoration, total_load, TIE_LINES, \
    downstream_deenergized_buses, get_load_by_bus, ZONE_OF_BUS

net0 = build_base_net()
TOTAL_LOAD = total_load(net0)

# Which tie lines are "local" to each zone (candidate actions a zone agent
# would consider on its own, before escalating): tie line -> (from_bus,to_bus)
tie_geometry = {int(i): (int(net0.line.at[i, 'from_bus']), int(net0.line.at[i, 'to_bus']))
                for i in TIE_LINES}


def zone_local_ties(faulted_line):
    """Ties whose endpoints lie in the same zone(s) as the de-energized buses."""
    deenerg = downstream_deenergized_buses(net0, faulted_line)
    zones_affected = {ZONE_OF_BUS[b] for b in deenerg}
    local = []
    for t, (fb, tb) in tie_geometry.items():
        if ZONE_OF_BUS[fb] in zones_affected or ZONE_OF_BUS[tb] in zones_affected:
            local.append(t)
    return local, zones_affected


def centralized_restore(faulted_line):
    # Baseline: no tie switches closed (whatever remains connected to the
    # substation without any reconfiguration action).
    feas0, restored0, _ = try_restoration(net0, faulted_line, [])
    best_restored, best_action, n_tries = (restored0 if feas0 else 0.0), [], 1
    for r in range(1, len(TIE_LINES) + 1):
        for combo in itertools.combinations(TIE_LINES, r):
            n_tries += 1
            feas, restored, _ = try_restoration(net0, faulted_line, list(combo))
            if feas and restored > best_restored:
                best_restored, best_action = restored, list(combo)
    return best_restored, best_action, n_tries


def decentralized_restore(faulted_line, max_rounds=2):
    """Round 1: local zone agent(s) try their own candidate ties only.
    Round 2 (escalation): if still infeasible/insufficient, broaden to
    one-hop neighbor ties (models a single round of agent-to-agent
    communication)."""
    local_ties, zones_affected = zone_local_ties(faulted_line)
    messages = len(zones_affected)  # zone agent(s) detect fault, alert neighbors

    # Every agent always knows its own baseline (do-nothing) state --
    # this requires no communication, so it is available at round 0.
    feas0, restored0, _ = try_restoration(net0, faulted_line, [])
    best_restored, best_action, n_tries = (restored0 if feas0 else 0.0), [], 1

    candidates = []
    for r in range(1, min(2, len(local_ties)) + 1):
        candidates += list(itertools.combinations(local_ties, r))
    for combo in candidates:
        n_tries += 1
        feas, restored, _ = try_restoration(net0, faulted_line, list(combo))
        if feas and restored > best_restored:
            best_restored, best_action = restored, list(combo)

    rounds_used = 1
    if best_restored < TOTAL_LOAD - 1e-6 and max_rounds > 1:
        # Escalate: broadcast a help request; every other zone agent
        # proposes its OWN single tie-switch action in response (a
        # realistic bound on a single additional communication round --
        # agents do not jointly search multi-switch combinations, since
        # that would require centralized coordination).
        messages += len(TIE_LINES)  # broadcast + one response per tie-owning agent
        rounds_used = 2
        for t in TIE_LINES:
            n_tries += 1
            feas, restored, _ = try_restoration(net0, faulted_line, [t])
            if feas and restored > best_restored:
                best_restored, best_action = restored, [t]

    return best_restored, best_action, n_tries, messages, rounds_used


results = []
for line in range(32):
    deenerg = downstream_deenergized_buses(net0, line)
    if len(deenerg) == 0:
        continue  # fault does not island any bus (radial leaf redundancy)
    cen_restored, cen_action, cen_tries = centralized_restore(line)
    dec_restored, dec_action, dec_tries, dec_msgs, dec_rounds = decentralized_restore(line)
    results.append({
        "faulted_line": line,
        "n_deenergized_buses": len(deenerg),
        "centralized_restored_mw": cen_restored,
        "centralized_tries": cen_tries,
        "decentralized_restored_mw": dec_restored,
        "decentralized_tries": dec_tries,
        "decentralized_messages": dec_msgs,
        "decentralized_rounds": dec_rounds,
    })

n_faults = len(results)
cen_pct = [r["centralized_restored_mw"] / TOTAL_LOAD * 100 for r in results]
dec_pct = [r["decentralized_restored_mw"] / TOTAL_LOAD * 100 for r in results]
cen_tries_avg = np.mean([r["centralized_tries"] for r in results])
dec_tries_avg = np.mean([r["decentralized_tries"] for r in results])
dec_msgs_avg = np.mean([r["decentralized_messages"] for r in results])

print(f"Total simulated fault scenarios (nontrivial): {n_faults}")
print(f"Centralized: mean restored = {np.mean(cen_pct):.2f}%  "
      f"(full restoration in {sum(1 for p in cen_pct if p>99.9)}/{n_faults} cases), "
      f"avg search evaluations = {cen_tries_avg:.1f}")
print(f"Decentralized: mean restored = {np.mean(dec_pct):.2f}%  "
      f"(full restoration in {sum(1 for p in dec_pct if p>99.9)}/{n_faults} cases), "
      f"avg search evaluations = {dec_tries_avg:.1f}, avg messages = {dec_msgs_avg:.1f}")

with open("/home/claude/smartgrid_paper/data/exp1_restoration.json", "w") as f:
    json.dump({
        "total_load_mw": TOTAL_LOAD, "n_faults": n_faults, "results": results,
        "summary": {
            "centralized_mean_restored_pct": float(np.mean(cen_pct)),
            "decentralized_mean_restored_pct": float(np.mean(dec_pct)),
            "centralized_avg_tries": float(cen_tries_avg),
            "decentralized_avg_tries": float(dec_tries_avg),
            "decentralized_avg_messages": float(dec_msgs_avg),
        }
    }, f, indent=2)
print("Saved exp1_restoration.json")
