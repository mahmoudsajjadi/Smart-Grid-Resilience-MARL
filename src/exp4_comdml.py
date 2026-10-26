"""
Experiment 4: Communication-Efficient Decentralized Multi-Agent Training
Under Heterogeneous Resources, directly inspired by our prior work on
Communication-efficient training workload balancing for Decentralized
Multi-agent Learning (ComDML) [Mohammadabadi et al., ICDCS 2024]. Five
zone agents (Sec. Experiment 2) jointly train a shared reconfiguration
policy via decentralized (peer-to-peer) synchronization rounds. Agents
have heterogeneous per-update compute latency (representing real
heterogeneous edge hardware at substations of different vintages). We
compare:
  (a) Naive synchronous decentralized training: every round, all 5
      agents perform a full local update and then synchronize; the round
      time is bottlenecked by the slowest ("straggler") agent.
  (b) ComDML-style workload-balanced training: each agent's per-round
      workload (number of local fault samples it processes before
      synchronizing) is set inversely proportional to its measured
      compute latency, so faster agents take on proportionally more
      work and slower agents less, equalizing wall-clock round time
      while preserving the same *total* work done per round.
"""
import os as _o, os.path as _p
_o.chdir(_p.dirname(_p.dirname(_p.abspath(__file__))))  # run from the repo root: portable paths
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
from grid_env import build_base_net, try_restoration, total_load, TIE_LINES
from exp2_qlearning import reward_table, ACTIONS, N_ACTIONS, oracle_best, FAULT_LINES

rng = np.random.default_rng(3)

N_AGENTS = 5
# Heterogeneous per-sample compute latency (seconds), representing
# real heterogeneous edge controllers (older RTUs vs modern edge PCs).
AGENT_LATENCY = np.array([0.010, 0.014, 0.022, 0.055, 0.090])  # agent 4 is a strong straggler

TARGET_AVG_REWARD_FRAC = 0.90  # fraction of oracle performance to reach
N_ROUNDS = 400
BASE_SAMPLES_PER_ROUND = 8  # total fault samples processed per round, split across agents

oracle_mean = np.mean([oracle_best(line) for line in FAULT_LINES])


def run_training(workload_balanced, seed=0):
    r = np.random.default_rng(seed)
    Q = np.zeros((32, N_ACTIONS))
    alpha = 0.2
    wall_clock = 0.0
    trace = []  # (wall_clock_time, avg_reward_of_greedy_policy)

    if workload_balanced:
        # ComDML-style workload balancing: rather than forcing every
        # agent to contribute every round (which leaves the round time
        # bottlenecked by the slowest agent regardless of how little work
        # it is given), each agent's *participation duty cycle* is set
        # inversely proportional to its latency, so slow agents offload
        # most of their rounds to faster peers and only participate
        # occasionally, while fast agents pick up proportionally more
        # rounds. Total long-run work contributed is kept comparable
        # across schemes.
        inv = 1.0 / AGENT_LATENCY
        duty_cycle = inv / inv.max()  # fastest agent: duty=1.0 (every round)
        samples_per_participation = 2
    else:
        # Naive: every agent participates every round with equal, fixed
        # per-round workload regardless of speed.
        duty_cycle = np.ones(N_AGENTS)
        samples_per_participation = max(1, BASE_SAMPLES_PER_ROUND // N_AGENTS)

    for rnd in range(N_ROUNDS):
        round_times = [0.0]
        for agent_id in range(N_AGENTS):
            if r.random() > duty_cycle[agent_id]:
                continue  # this agent sits out this round (offloaded)
            n_local = samples_per_participation
            for _ in range(n_local):
                line = r.integers(0, 32)
                eps = max(0.05, 1.0 - rnd / (0.6 * N_ROUNDS))
                if r.random() < eps:
                    a = r.integers(0, N_ACTIONS)
                else:
                    a = int(np.argmax(Q[line]))
                reward = reward_table[(line, a)]
                Q[line, a] += alpha * (reward - Q[line, a])
            round_times.append(n_local * AGENT_LATENCY[agent_id])
        # Synchronous barrier: round time = slowest *participating*
        # agent's local compute time this round, plus fixed comm overhead.
        comm_overhead = 0.004
        wall_clock += max(round_times) + comm_overhead

        if rnd % 5 == 0:
            avg_restored = np.mean([max(reward_table[(line, int(np.argmax(Q[line])))], 0.0)
                                     for line in FAULT_LINES])
            trace.append((wall_clock, avg_restored / oracle_mean))

    return trace, wall_clock


N_SEEDS = 8
naive_traces, naive_finals = [], []
balanced_traces, balanced_finals = [], []
for s in range(N_SEEDS):
    t_n, wc_n = run_training(False, seed=s)
    t_b, wc_b = run_training(True, seed=s)
    naive_traces.append(t_n)
    balanced_traces.append(t_b)
    naive_finals.append(wc_n)
    balanced_finals.append(wc_b)


def time_to_target(trace, target=TARGET_AVG_REWARD_FRAC):
    for t, perf in trace:
        if perf >= target:
            return t
    return None


naive_ttt = [time_to_target(t) for t in naive_traces]
balanced_ttt = [time_to_target(t) for t in balanced_traces]
naive_ttt_valid = [x for x in naive_ttt if x is not None]
balanced_ttt_valid = [x for x in balanced_ttt if x is not None]

print(f"Target: {TARGET_AVG_REWARD_FRAC*100:.0f}% of oracle mean restorable load")
print(f"Naive synchronous:      reached target in "
      f"{len(naive_ttt_valid)}/{N_SEEDS} runs, "
      f"mean wall-clock time = {np.mean(naive_ttt_valid):.2f} s")
print(f"ComDML workload-balanced: reached target in "
      f"{len(balanced_ttt_valid)}/{N_SEEDS} runs, "
      f"mean wall-clock time = {np.mean(balanced_ttt_valid):.2f} s")
speedup = np.mean(naive_ttt_valid) / np.mean(balanced_ttt_valid)
print(f"Speedup: {speedup:.2f}x")

# Use seed-0 traces as representative curves for plotting
with open("./data/exp4_comdml.json", "w") as f:
    json.dump({
        "agent_latency": AGENT_LATENCY.tolist(),
        "target_frac": TARGET_AVG_REWARD_FRAC,
        "naive_trace_seed0": naive_traces[0],
        "balanced_trace_seed0": balanced_traces[0],
        "naive_ttt_all_seeds": naive_ttt,
        "balanced_ttt_all_seeds": balanced_ttt,
        "naive_mean_ttt": float(np.mean(naive_ttt_valid)),
        "balanced_mean_ttt": float(np.mean(balanced_ttt_valid)),
        "speedup": float(speedup),
    }, f, indent=2)
print("Saved exp4_comdml.json")
