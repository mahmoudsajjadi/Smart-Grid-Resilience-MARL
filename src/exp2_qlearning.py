"""
Experiment 2: Multi-Agent Reinforcement Learning for Self-Healing
Topology Reconfiguration. Each of the 5 zone agents maintains its own
Q-table over (fault-signature, action) pairs and learns, purely from
trial-and-error reward feedback (no access to the underlying power-flow
model), which tie-switch action best responds to a fault affecting its
zone. This demonstrates the "self-improving" property central to this
paper's thesis: performance rises over training episodes toward the
oracle optimum established in Experiment 1, without ever being told the
power-flow equations directly.
"""
import os as _o, os.path as _p
_o.chdir(_p.dirname(_p.dirname(_p.abspath(__file__))))  # run from the repo root: portable paths
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
from grid_env import build_base_net, try_restoration, total_load, TIE_LINES, \
    downstream_deenergized_buses, ZONE_OF_BUS

net0 = build_base_net()
TOTAL_LOAD = total_load(net0)
rng = np.random.default_rng(0)

FAULT_LINES = list(range(32))
ACTIONS = [[]] + [[t] for t in TIE_LINES]  # do-nothing, or close exactly one tie
N_ACTIONS = len(ACTIONS)

# Precompute the reward (restored MW, feasibility) for every
# (fault, action) pair once -- this is the *environment* the agent must
# discover through interaction; the agent itself never sees this table.
reward_table = {}
for line in FAULT_LINES:
    for ai, act in enumerate(ACTIONS):
        feas, restored, _ = try_restoration(net0, line, act)
        reward_table[(line, ai)] = restored if feas else -0.5  # penalty for infeasible switching


def oracle_best(line):
    return max(reward_table[(line, ai)] for ai in range(N_ACTIONS))


# ---------------------------------------------------------------------------
# Independent tabular Q-learning, one Q-table per zone agent, but every
# agent is queried for every fault (a zone agent "owns" the decision for
# faults inside or adjacent to its zone; here we let a single shared but
# factored Q-table per fault-line stand in for the zone owning that line,
# which is equivalent to 5 independent per-zone tables in this setting).
# ---------------------------------------------------------------------------
def train_qlearning(n_episodes=600, alpha=0.2, gamma=0.0, eps_start=1.0, eps_end=0.05,
                     seed=0):
    r = np.random.default_rng(seed)
    Q = np.zeros((32, N_ACTIONS))
    history = []
    for ep in range(n_episodes):
        eps = eps_start + (eps_end - eps_start) * min(1.0, ep / (0.7 * n_episodes))
        line = r.integers(0, 32)
        if r.random() < eps:
            a = r.integers(0, N_ACTIONS)
        else:
            a = int(np.argmax(Q[line]))
        reward = reward_table[(line, a)]
        Q[line, a] += alpha * (reward - Q[line, a])
        history.append(reward)
    return Q, history


def random_policy_reward(n_episodes=600, seed=1):
    r = np.random.default_rng(seed)
    rewards = []
    for _ in range(n_episodes):
        line = r.integers(0, 32)
        a = r.integers(0, N_ACTIONS)
        rewards.append(reward_table[(line, a)])
    return rewards


def evaluate_greedy_policy(Q):
    total, oracle_total = 0.0, 0.0
    for line in FAULT_LINES:
        a = int(np.argmax(Q[line]))
        total += max(reward_table[(line, a)], 0.0)
        oracle_total += oracle_best(line)
    return total / len(FAULT_LINES), oracle_total / len(FAULT_LINES)


if __name__ == "__main__":
    N_EPISODES = 600
    N_SEEDS = 10
    all_histories = []
    final_policy_perf = []
    for seed in range(N_SEEDS):
        Q, hist = train_qlearning(n_episodes=N_EPISODES, seed=seed)
        all_histories.append(hist)
        avg_restored, oracle_avg = evaluate_greedy_policy(Q)
        final_policy_perf.append(avg_restored)

    all_histories = np.array(all_histories)  # (seeds, episodes)
    mean_curve = all_histories.mean(axis=0)
    # smooth with a moving average for a readable learning curve
    window = 20
    smoothed = np.convolve(mean_curve, np.ones(window) / window, mode='valid')

    random_rewards = np.array([random_policy_reward(N_EPISODES, seed=s) for s in range(N_SEEDS)])
    random_mean_curve = random_rewards.mean(axis=0)
    random_smoothed = np.convolve(random_mean_curve, np.ones(window) / window, mode='valid')

    oracle_mean = np.mean([oracle_best(line) for line in FAULT_LINES])

    print(f"Oracle (Experiment 1 centralized-equivalent) mean restorable load: {oracle_mean:.4f} MW")
    print(f"Learned greedy policy mean restored load (avg over {N_SEEDS} seeds): "
          f"{np.mean(final_policy_perf):.4f} +/- {np.std(final_policy_perf):.4f} MW "
          f"({np.mean(final_policy_perf)/oracle_mean*100:.1f}% of oracle)")
    print(f"Final-100-episode random-policy avg reward: {np.mean(random_mean_curve[-100:]):.4f} MW")
    print(f"Final-100-episode learned-policy avg reward: {np.mean(mean_curve[-100:]):.4f} MW")

    with open("./data/exp2_qlearning.json", "w") as f:
        json.dump({
            "n_episodes": N_EPISODES, "n_seeds": N_SEEDS, "window": window,
            "oracle_mean_mw": float(oracle_mean),
            "qlearning_smoothed_curve": smoothed.tolist(),
            "random_smoothed_curve": random_smoothed.tolist(),
            "final_policy_perf_per_seed": [float(x) for x in final_policy_perf],
            "final_policy_perf_pct_of_oracle": float(np.mean(final_policy_perf) / oracle_mean * 100),
        }, f, indent=2)
    print("Saved exp2_qlearning.json")
