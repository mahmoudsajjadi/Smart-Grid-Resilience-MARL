import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make_figure():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.2, 3.1), dpi=300)

    agents = [f"Agent {i}" for i in range(1, 6)]
    y_pos = np.arange(len(agents))[::-1] # Agent 1 at top

    # --- Subplot (a): Naive Synchronous (Fixed Load) ---
    equal_work = 2.4
    barrier_x = 4.0

    bars_active = ax1.barh(y_pos, [equal_work]*5, height=0.58, 
                           color="#f8d7da", edgecolor="#721c24", linewidth=1.1)
    bars_idle = ax1.barh(y_pos, [barrier_x - equal_work]*5, left=[equal_work]*5, height=0.58,
                         color="white", edgecolor="#dc3545", hatch="//", linewidth=1.1)

    for y in y_pos:
        ax1.text(equal_work/2, y, "Equal Task", ha="center", va="center", 
                 fontsize=9.0, fontweight="bold", color="#721c24")

    ax1.vlines(barrier_x, -0.4, 4.35, color="#c5221f", linestyle="--", linewidth=2.0)
    ax1.text(barrier_x, 4.55, "Sync Barrier\n(Stragglers Delay All)", 
             ha="center", va="bottom", fontsize=8.6, fontweight="bold", color="#c5221f")

    ax1.set_title("(a) Naive Synchronous (Fixed Work)", fontsize=9.6, fontweight="bold", pad=28)
    ax1.set_xlim(-1.2, 4.8)
    ax1.set_ylim(-0.6, 5.7)
    ax1.axis("off")
    for y, ag in zip(y_pos, agents):
        ax1.text(-0.15, y, ag, ha="right", va="center", fontsize=9.2, fontweight="bold", color="#222222")

    # --- Subplot (b): ComDML (Balanced Load) ---
    loads = [5.2, 4.5, 3.4, 2.2, 1.2]
    bar_lens = [4.0 * (l / 5.2) for l in loads]
    bars_balanced = ax2.barh(y_pos, bar_lens, height=0.58,
                             color="#d4edda", edgecolor="#155724", linewidth=1.1)

    for y, bl, l in zip(y_pos, bar_lens, loads):
        if l >= 3.0:  # Agents 1, 2, 3 inside; Agents 4, 5 outside
            ax2.text(bl/2, y, f"Load: {l:.1f}\u00d7", ha="center", va="center", 
                     fontsize=9.0, fontweight="bold", color="#155724")
        else:
            ax2.text(bl + 0.15, y, f"Load: {l:.1f}\u00d7", ha="left", va="center", 
                     fontsize=9.0, fontweight="bold", color="#155724")

    ax2.vlines(4.0, -0.4, 4.35, color="#1e7e34", linestyle="-", linewidth=2.0)
    ax2.text(4.0, 4.55, "Optimized Barrier\n(Zero Idle / Perfect Overlap)", 
             ha="center", va="bottom", fontsize=8.6, fontweight="bold", color="#1e7e34")

    ax2.set_title("(b) ComDML (Proportionally Balanced)", fontsize=9.6, fontweight="bold", pad=28)
    ax2.set_xlim(-1.1, 5.8)
    ax2.set_ylim(-0.6, 5.7)
    ax2.axis("off")
    for y, ag in zip(y_pos, agents):
        ax2.text(-0.15, y, ag, ha="right", va="center", fontsize=9.2, fontweight="bold", color="#222222")

    plt.subplots_adjust(left=0.05, right=0.96, top=0.82, bottom=0.04, wspace=0.25)
    plt.savefig("figures/fig10_comdml_architecture.pdf", bbox_inches="tight", pad_inches=0.08)
    plt.savefig("figures/fig10_comdml_architecture.png", dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close()
    print("Figure 5 (ComDML architecture) updated with extra bold large text.")

if __name__ == "__main__":
    make_figure()
