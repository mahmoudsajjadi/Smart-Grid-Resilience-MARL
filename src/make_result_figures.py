import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 12, 
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.spines.top": False, 
    "axes.spines.right": False, 
    "figure.dpi": 150
})
FIGDIR = "figures"
DATADIR = "data"

def load(name):
    with open(f"{DATADIR}/{name}") as f:
        return json.load(f)

# ===========================================================================
# Figure 3: Experiment 1 - restoration quality & search-cost comparison
# ===========================================================================
d1 = load("exp1_restoration.json")
s = d1["summary"]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))

ax = axes[0]
bars = ax.bar(["Centralized", "Decentralized\n(multi-agent)"],
              [s["centralized_mean_restored_pct"], s["decentralized_mean_restored_pct"]],
              color=["#8172b2", "#55a868"], width=0.55)
for b, v in zip(bars, [s["centralized_mean_restored_pct"], s["decentralized_mean_restored_pct"]]):
    ax.text(b.get_x() + b.get_width()/2, v + 1.2, f"{v:.1f}%", ha="center", fontsize=11.5, fontweight="bold")
ax.set_ylabel("Mean load restored (%)", fontsize=12)
ax.set_ylim(0, 100)
ax.set_title("(a) Restoration quality (identical)", fontsize=13, fontweight="bold")
ax.tick_params(labelsize=11)

ax = axes[1]
bars = ax.bar(["Centralized", "Decentralized\n(multi-agent)"],
              [s["centralized_avg_tries"], s["decentralized_avg_tries"]],
              color=["#8172b2", "#55a868"], width=0.55)
for b, v in zip(bars, [s["centralized_avg_tries"], s["decentralized_avg_tries"]]):
    ax.text(b.get_x() + b.get_width()/2, v + 0.6, f"{v:.1f}", ha="center", fontsize=11.5, fontweight="bold")
ax.set_ylabel("Avg. feasibility evaluations per fault", fontsize=12)
ax.set_title(f"(b) Search cost (\u221272% fewer evaluations)", fontsize=13, fontweight="bold")
ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig3_exp1_restoration.pdf")
plt.savefig(f"{FIGDIR}/fig3_exp1_restoration.png", dpi=150)
plt.close()

# ===========================================================================
# Figure 4: Experiment 2 - self-improvement learning curve
# ===========================================================================
d2 = load("exp2_qlearning.json")
q_curve = np.array(d2["qlearning_smoothed_curve"])
r_curve = np.array(d2["random_smoothed_curve"])
oracle = d2["oracle_mean_mw"]
episodes = np.arange(len(q_curve))

fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
ax.plot(episodes, q_curve, color="#4c72b0", lw=2.2, label="Multi-agent Q-learning (this work)")
ax.plot(episodes, r_curve, color="#c44e52", lw=1.8, linestyle="--", label="Random policy baseline")
ax.axhline(oracle, color="#333333", linestyle=":", lw=1.6, label="Oracle (Experiment 1 optimum)")
ax.set_xlabel("Training episode (20-episode moving average)", fontsize=12)
ax.set_ylabel("Mean restored load (MW)", fontsize=12)
ax.set_title("Self-Improvement of the Multi-Agent Restoration Policy", fontsize=13, fontweight="bold")
ax.set_ylim(0.2, 3.45)
ax.legend(fontsize=10.5, loc="upper left", bbox_to_anchor=(0.04, 0.94),
          frameon=True, facecolor="white", framealpha=0.95, edgecolor="#d0d0d0")
ax.tick_params(labelsize=11)
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig4_exp2_learning_curve.pdf")
plt.savefig(f"{FIGDIR}/fig4_exp2_learning_curve.png", dpi=300)
plt.close()

# ===========================================================================
# Figure 5: Experiment 3 - coordinated vs uncoordinated storage dispatch
# ===========================================================================
d3 = load("exp3_storage.json")
s3 = d3["summary"]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))

ax = axes[0]
vals = [s3["uncoordinated_critical_served_pct"], s3["coordinated_critical_served_pct"]]
bars = ax.bar(["Uncoordinated", "Coordinated\n(multi-agent)"], vals, color=["#c44e52", "#55a868"], width=0.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 0.15, f"{v:.1f}%", ha="center", fontsize=11.5, fontweight="bold")
ax.set_ylabel("Critical-load hours fully served (%)", fontsize=12)
ax.set_title("(a) Reliability of critical-load service", fontsize=13, fontweight="bold")
ax.tick_params(labelsize=11)

ax = axes[1]
vals2 = [s3["uncoordinated_critical_energy_kwh"], s3["coordinated_critical_energy_kwh"]]
bars = ax.bar(["Uncoordinated", "Coordinated\n(multi-agent)"], vals2, color=["#c44e52", "#55a868"], width=0.55)
for b, v in zip(bars, vals2):
    ax.text(b.get_x() + b.get_width()/2, v + 9, f"{v:.0f} kWh", ha="center", fontsize=11.5, fontweight="bold")
ax.set_ylabel("Total critical-load energy delivered (kWh)", fontsize=12)
ax.set_title("(b) Aggregate energy throughput", fontsize=13, fontweight="bold")
ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig5_exp3_storage.pdf")
plt.savefig(f"{FIGDIR}/fig5_exp3_storage.png", dpi=150)
plt.close()

print("Result figures 3, 4, 5 re-generated with larger text.")
