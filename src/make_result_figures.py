import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
FIGDIR = "/home/claude/smartgrid_paper/figures"
DATADIR = "/home/claude/smartgrid_paper/data"


def load(name):
    with open(f"{DATADIR}/{name}") as f:
        return json.load(f)


# ===========================================================================
# Figure 3: Experiment 1 - restoration quality & search-cost comparison
# ===========================================================================
d1 = load("exp1_restoration.json")
s = d1["summary"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))

ax = axes[0]
bars = ax.bar(["Centralized", "Decentralized\n(multi-agent)"],
              [s["centralized_mean_restored_pct"], s["decentralized_mean_restored_pct"]],
              color=["#8172b2", "#55a868"], width=0.55)
for b, v in zip(bars, [s["centralized_mean_restored_pct"], s["decentralized_mean_restored_pct"]]):
    ax.text(b.get_x() + b.get_width()/2, v + 1, f"{v:.1f}%", ha="center", fontsize=10)
ax.set_ylabel("Mean load restored (%)")
ax.set_ylim(0, 100)
ax.set_title("(a) Restoration quality (identical)")

ax = axes[1]
bars = ax.bar(["Centralized", "Decentralized\n(multi-agent)"],
              [s["centralized_avg_tries"], s["decentralized_avg_tries"]],
              color=["#8172b2", "#55a868"], width=0.55)
for b, v in zip(bars, [s["centralized_avg_tries"], s["decentralized_avg_tries"]]):
    ax.text(b.get_x() + b.get_width()/2, v + 0.5, f"{v:.1f}", ha="center", fontsize=10)
ax.set_ylabel("Avg. feasibility evaluations per fault")
ax.set_title(f"(b) Search cost (\u221272% fewer evaluations)")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig3_exp1_restoration.pdf")
plt.close()

# ===========================================================================
# Figure 4: Experiment 2 - self-improvement learning curve
# ===========================================================================
d2 = load("exp2_qlearning.json")
q_curve = np.array(d2["qlearning_smoothed_curve"])
r_curve = np.array(d2["random_smoothed_curve"])
oracle = d2["oracle_mean_mw"]
episodes = np.arange(len(q_curve))

fig, ax = plt.subplots(figsize=(7, 4.6))
ax.plot(episodes, q_curve, color="#4c72b0", lw=2, label="Multi-agent Q-learning (this work)")
ax.plot(episodes, r_curve, color="#c44e52", lw=1.6, linestyle="--", label="Random policy baseline")
ax.axhline(oracle, color="#333333", linestyle=":", lw=1.4, label="Oracle (Experiment 1 optimum)")
ax.set_xlabel("Training episode (20-episode moving average)")
ax.set_ylabel("Mean restored load (MW)")
ax.set_title("Self-Improvement of the Multi-Agent Restoration Policy")
ax.legend(fontsize=9, loc="lower right")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig4_exp2_learning_curve.pdf")
plt.close()

# ===========================================================================
# Figure 5: Experiment 3 - coordinated vs uncoordinated storage dispatch
# ===========================================================================
d3 = load("exp3_storage.json")
s3 = d3["summary"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))

ax = axes[0]
vals = [s3["uncoordinated_critical_served_pct"], s3["coordinated_critical_served_pct"]]
bars = ax.bar(["Uncoordinated", "Coordinated\n(multi-agent)"], vals, color=["#c44e52", "#55a868"], width=0.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.15, f"{v:.1f}%", ha="center", fontsize=10)
ax.set_ylabel("Critical-load hours fully served (%)")
ax.set_title("(a) Reliability of critical-load service")

ax = axes[1]
vals2 = [s3["uncoordinated_critical_energy_kwh"], s3["coordinated_critical_energy_kwh"]]
bars = ax.bar(["Uncoordinated", "Coordinated\n(multi-agent)"], vals2, color=["#c44e52", "#55a868"], width=0.55)
for b, v in zip(bars, vals2):
    ax.text(b.get_x() + b.get_width()/2, v + 8, f"{v:.0f} kWh", ha="center", fontsize=10)
ax.set_ylabel("Total critical-load energy delivered (kWh)")
ax.set_title("(b) Aggregate energy throughput")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig5_exp3_storage.pdf")
plt.close()

# SoC traces (example run)
fig, ax = plt.subplots(figsize=(7, 4.4))
for label, key, style in [("Uncoordinated", "uncoordinated_example_trace", "--"),
                            ("Coordinated", "coordinated_example_trace", "-")]:
    trace = d3[key]["soc_trace"]
    for i, (bus, series) in enumerate(trace.items()):
        ax.plot(range(len(series)), np.array(series) * 1000, style,
                label=f"{label}, battery @ bus {bus}" if i == 0 else None,
                color="#c44e52" if label == "Uncoordinated" else "#55a868", alpha=0.5 + 0.15*i)
ax.set_xlabel("Hour of islanding event")
ax.set_ylabel("Battery state of charge (kWh)")
ax.set_title("Battery State-of-Charge Trajectories During Islanding")
ax.legend(fontsize=8.5)
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig6_exp3_soc_traces.pdf")
plt.close()

# ===========================================================================
# Figure 7: Experiment 4 - ComDML-style workload balancing convergence
# ===========================================================================
d4 = load("exp4_comdml.json")
naive = np.array(d4["naive_trace_seed0"])
balanced = np.array(d4["balanced_trace_seed0"])
target = d4["target_frac"]

fig, ax = plt.subplots(figsize=(7, 4.6))
ax.plot(naive[:, 0], naive[:, 1] * 100, color="#c44e52", lw=2, label="Naive synchronous (even split)")
ax.plot(balanced[:, 0], balanced[:, 1] * 100, color="#4c72b0", lw=2,
        label="ComDML-style workload-balanced")
ax.axhline(target * 100, color="#333333", linestyle=":", lw=1.3, label=f"Target ({target*100:.0f}% of oracle)")
ax.set_xlabel("Wall-clock training time (s)")
ax.set_ylabel("Policy performance (% of oracle)")
ax.set_title(f"Decentralized Training Under Heterogeneous Agents\n"
             f"(speedup: {d4['speedup']:.2f}$\\times$ to reach target)")
ax.legend(fontsize=9, loc="lower right")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig7_exp4_comdml.pdf")
plt.close()

# ===========================================================================
# Figure 8: Experiment 5 - scalability
# ===========================================================================
d5 = load("exp5_scalability.json")
networks = list(d5.keys())
labels = ["IEEE 33-bus\n(33 buses, 5 ties)", "Oberrhein MV\n(179 buses, 6 ties)"]
cen_times = [d5[n]["centralized_time_s"] * 1000 for n in networks]
dec_times = [d5[n]["decentralized_time_s"] * 1000 for n in networks]
speedups = [d5[n]["speedup"] for n in networks]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
ax = axes[0]
x = np.arange(len(networks))
w = 0.32
ax.bar(x - w/2, cen_times, width=w, label="Centralized (exhaustive)", color="#8172b2")
ax.bar(x + w/2, dec_times, width=w, label="Decentralized (local)", color="#55a868")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Restoration decision time (ms, log scale)")
ax.set_title("(a) Absolute decision time")
ax.legend(fontsize=8.5)

ax = axes[1]
ax.plot([d5[n]["n_buses"] for n in networks], speedups, "o-", color="#c44e52", ms=10, lw=2)
for n in networks:
    ax.annotate(f"{d5[n]['speedup']:.1f}$\\times$", (d5[n]["n_buses"], d5[n]["speedup"]),
                textcoords="offset points", xytext=(8, 6), fontsize=9)
ax.set_xlabel("Network size (number of buses)")
ax.set_ylabel("Decentralized speedup factor")
ax.set_title("(b) Speedup grows with network scale")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig8_exp5_scalability.pdf")
plt.close()

print("All result figures (3-8) written.")
