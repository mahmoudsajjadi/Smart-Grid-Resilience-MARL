import os as _o, os.path as _p
_o.chdir(_p.dirname(_p.dirname(_p.abspath(__file__))))  # run from the repo root: portable paths
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.insert(0, "./code")
from grid_env import build_base_net, TIE_LINES, ZONE_OF_BUS, N_ZONES

plt.rcParams.update({"font.size": 10, "figure.dpi": 150})
FIGDIR = "./figures"

net = build_base_net()

G = nx.Graph()
G.add_nodes_from(range(len(net.bus)))
for _, row in net.line.iterrows():
    G.add_edge(int(row.from_bus), int(row.to_bus), tie=not row.in_service)

# Layout: use a tree layout approximation via networkx spring layout seeded
# for reproducibility, then nudge the substation (bus 0) to the top.
pos = nx.kamada_kawai_layout(G)
# flip/orient so bus 0 is roughly at top
pos = {n: (x, y) for n, (x, y) in pos.items()}

zone_colors = ["#f4cccc", "#d9ead3", "#c9daf8", "#fce5cd", "#d9d2e9"]
node_colors = [zone_colors[ZONE_OF_BUS[n]] for n in G.nodes()]

fig, ax = plt.subplots(figsize=(9, 7.5))
normal_edges = [(u, v) for u, v, d in G.edges(data=True) if not d["tie"]]
tie_edges = [(u, v) for u, v, d in G.edges(data=True) if d["tie"]]

nx.draw_networkx_edges(G, pos, edgelist=normal_edges, ax=ax, edge_color="#555555", width=1.6)
nx.draw_networkx_edges(G, pos, edgelist=tie_edges, ax=ax, edge_color="#cc0000",
                        width=1.8, style="dashed")
nx.draw_networkx_nodes(G, pos, node_color=node_colors, edgecolors="#333333",
                        linewidths=0.8, node_size=420, ax=ax)
nx.draw_networkx_labels(G, pos, labels={n: str(n) for n in G.nodes()}, font_size=7, ax=ax)

# highlight substation
nx.draw_networkx_nodes(G, pos, nodelist=[0], node_color="#ffd966", edgecolors="black",
                        linewidths=1.6, node_size=550, ax=ax)

from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0], [0], color="#555555", lw=1.6, label="Sectionalizing line (normally closed)"),
    Line2D([0], [0], color="#cc0000", lw=1.8, linestyle="dashed", label="Tie switch (normally open)"),
    Line2D([0], [0], marker='o', color='w', markerfacecolor="#ffd966", markeredgecolor="black",
           markersize=11, label="Substation (bus 0)"),
]
for zi in range(N_ZONES):
    legend_elems.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=zone_colors[zi],
                                markeredgecolor="#333333", markersize=10, label=f"Zone {zi+1} agent"))
ax.legend(handles=legend_elems, loc="upper center", bbox_to_anchor=(0.5, -0.02),
          ncol=3, fontsize=7.8, frameon=False)

ax.set_title("IEEE 33-Bus Feeder: Agent Zones and Tie Switches\n(Baran & Wu, 1989; via pandapower case33bw)",
             fontsize=11.5)
ax.axis("off")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/fig2_topology.pdf")
plt.close()
print("Figure 2 (topology) written.")
