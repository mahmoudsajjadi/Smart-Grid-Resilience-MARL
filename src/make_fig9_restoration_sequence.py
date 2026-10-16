import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def make_figure():
    fig, ax = plt.subplots(figsize=(6.2, 6.8), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12.2)
    ax.axis("off")

    # Title
    ax.text(5.0, 11.7, "Decentralized Multi-Agent Restoration Sequence", 
            fontsize=10.5, fontweight="bold", ha="center", va="center")

    steps = [
        {
            "num": "Step 1: Fault Occurs in Affected Feeder Section",
            "desc": "Local protection trips sectionalizer; downstream buses de-energized",
            "bg": "#fce8e6", "border": "#c5221f"
        },
        {
            "num": "Step 2: Local Agent Fast Search (Round 1)",
            "desc": "Affected zone agent evaluates immediate local tie switches within 200 ms",
            "bg": "#e8f0fe", "border": "#1a73e8"
        },
        {
            "num": "Step 3: Decision Gate: All Priority Loads Restored?",
            "desc": "Check restoration status [ If NO \u2192 Escalate to Round 2 | If YES \u2192 Validate & Execute ]",
            "bg": "#fef7e0", "border": "#d97706"
        },
        {
            "num": "Step 4: Round 2 Multi-Agent Escalation (Broadcast)",
            "desc": "Help request broadcasted to adjacent peer zone agents (Zones 2\u20135)",
            "bg": "#f3e8fd", "border": "#7b1fa2"
        },
        {
            "num": "Step 5: Neighboring Agents Propose Candidate Switching Actions",
            "desc": "Each peer agent independently checks local capacity and proposes feasible tie closures",
            "bg": "#e1f5fe", "border": "#0288d1"
        },
        {
            "num": "Step 6: Substation Layer AC Power-Flow Validation",
            "desc": "Full Newton-Raphson check validates radiality, voltage bounds\n(0.95\u20131.05 p.u.), and line thermal limits",
            "bg": "#e6f4ea", "border": "#137333"
        }
    ]

    box_w = 9.4
    box_h = 1.30
    box_x = 0.3
    y_starts = [10.0, 8.2, 6.4, 4.6, 2.8, 0.8]

    for i, (s, y) in enumerate(zip(steps, y_starts)):
        h = box_h if i < 5 else 1.45
        patch = FancyBboxPatch((box_x, y), box_w, h, 
                               boxstyle="round,pad=0.01,rounding_size=0.05",
                               facecolor=s["bg"], edgecolor=s["border"], linewidth=1.3)
        ax.add_patch(patch)
        
        # Header text
        ax.text(box_x + box_w/2, y + h * 0.68, s["num"], 
                ha="center", va="center", fontsize=9.2, fontweight="bold", color="#111111")
        # Description text
        desc_y = y + (h * 0.32 if i < 5 else h * 0.28)
        ax.text(box_x + box_w/2, desc_y, s["desc"], 
                ha="center", va="center", fontsize=8.0, fontweight="normal", color="#333333")
        
        # Arrow to next box
        if i < len(steps) - 1:
            next_y = y_starts[i+1] + (box_h if i+1 < 5 else 1.45)
            arr = FancyArrowPatch((box_x + box_w/2, y), (box_x + box_w/2, next_y),
                                  arrowstyle="-|>", mutation_scale=12, color="#444444", lw=1.3)
            ax.add_patch(arr)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    plt.savefig("figures/fig9_restoration_sequence.pdf")
    plt.savefig("figures/fig9_restoration_sequence.png", dpi=300)
    plt.close()
    print("Figure 4 (restoration sequence) regenerated.")

if __name__ == "__main__":
    make_figure()
