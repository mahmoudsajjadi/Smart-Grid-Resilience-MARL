import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

plt.rcParams.update({"font.size": 10, "figure.dpi": 150})
FIGDIR = "/home/claude/smartgrid_paper/figures"


def box(ax, x, y, w, h, text, color="#cfe2f3", fontsize=9, edgecolor="#333333"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                        facecolor=color, edgecolor=edgecolor, linewidth=1.1)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize, wrap=True)


def arrow(ax, xy1, xy2, color="#333333", style="<|-|>", lw=1.2):
    a = FancyArrowPatch(xy1, xy2, arrowstyle=style, mutation_scale=12,
                         color=color, linewidth=lw)
    ax.add_patch(a)


fig, ax = plt.subplots(figsize=(11, 7.5))
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis("off")

# Substation / centralized layer
box(ax, 8, 12.6, 6, 1.6, "Substation / Centralized\nSituational-Awareness Layer\n(full-network AC power-flow model)",
    "#fff2cc", fontsize=8.7)

# Five zone agents
zone_x = [0.5, 4.7, 8.9, 13.1, 17.3]
zone_labels = ["Zone Agent 1\n(feeder head)", "Zone Agent 2", "Zone Agent 3\n(+ battery)",
               "Zone Agent 4", "Zone Agent 5\n(+ battery)"]
colors = ["#f4cccc", "#d9ead3", "#c9daf8", "#fce5cd", "#d9d2e9"]
for x, lab, c in zip(zone_x, zone_labels, colors):
    box(ax, x, 9.2, 3.6, 1.7, lab, c, fontsize=8.3)
    arrow(ax, (x + 1.8, 10.9), (x + 1.8, 12.55), style="-|>", lw=1.0)

# tie-switch communication links between adjacent zone agents (peer-to-peer),
# placed in the clear gap between the zone-agent row and the substation row
for i in range(len(zone_x) - 1):
    x1 = zone_x[i] + 3.6
    x2 = zone_x[i + 1]
    arrow(ax, (x1, 11.6), (x2, 11.6), style="<|-|>", color="#999999", lw=1.3)
ax.text(11, 11.95, "peer-to-peer tie-switch coordination (limited-communication protocol)",
        fontsize=7.4, ha="center", style="italic", color="#555555")

# per-zone components: local RL policy, switches, DERs
comp_labels = ["Local Q-learning\npolicy\n(self-improving)", "Tie-switch\nactuators",
               "Local loads\n(incl. critical)", "Battery storage\n(zones 3, 5 only)"]
comp_colors = ["#ead1dc", "#e8e8e8", "#fbe4d5", "#d0e0e3"]
for zi, x in enumerate(zone_x):
    for ci, (clab, cc) in enumerate(zip(comp_labels, comp_colors)):
        if ci == 3 and zi not in (2, 4):
            continue
        cy = 6.6 - ci * 1.55 if ci < 3 else 1.95
        box(ax, x + 0.1, cy, 3.4, 1.25, clab, cc, fontsize=7.0)
    arrow(ax, (x + 1.8, 9.15), (x + 1.8, 7.9), style="-|>", lw=1.0)

ax.text(11, 14.6, "Multi-Agent Self-Healing Smart Grid Architecture", fontsize=13, ha="center")
ax.text(11, 0.4,
        "Vertical links: substation $\\leftrightarrow$ zone agent (fault detection, restoration confirmation). "
        "Horizontal links: zone $\\leftrightarrow$ zone (tie-switch requests, storage coordination, ComDML-style workload balancing).",
        fontsize=7.8, ha="center", color="#444444")

plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig1_architecture.pdf")
plt.close()
print("Figure 1 (architecture) written.")
