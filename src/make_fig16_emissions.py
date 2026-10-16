import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 10,
    "axes.labelsize": 10.8,
    "axes.titlesize": 11.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 8.5
})

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=300)

# ---------------- Panel (a): Decision time vs deadline ----------------
ax0 = axes[0]
networks = ["33-bus", "Oberrhein\n(179-bus)"]
cent_times = [939.8, 2648.4]
dec_times = [88.1, 124.1]

x = np.arange(len(networks))
width = 0.35

rects1 = ax0.bar(x - width/2, cent_times, width, label="Centralized (exhaustive)", color="#7a68a6", edgecolor="none")
rects2 = ax0.bar(x + width/2, dec_times, width, label="Decentralized (local)", color="#467821", edgecolor="none")

ax0.axhline(500, color="#d95f02", linestyle="--", linewidth=1.5, label="Assumed 500 ms deadline")

ax0.set_yscale("log")
ax0.set_ylim(40, 5000)
ax0.set_xticks(x)
ax0.set_xticklabels(networks)
ax0.set_ylabel("Restoration decision time (ms, log scale)")
ax0.set_title("(a) Decision time vs. automation deadline", fontweight="bold")
ax0.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=8.2)
ax0.grid(True, which="both", linestyle=":", alpha=0.35)

for rect in rects1:
    h = rect.get_height()
    ax0.annotate(f"{h:.0f} ms", xy=(rect.get_x() + rect.get_width()/2, h),
                 xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold", color="#4a3b70")

for rect in rects2:
    h = rect.get_height()
    ax0.annotate(f"{h:.0f} ms", xy=(rect.get_x() + rect.get_width()/2, h),
                 xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold", color="#2d5214")

# ---------------- Panel (b): Avoided emissions vs fallback delay ----------------
ax1 = axes[1]
T_fallback = np.array([15, 30, 45, 60, 90])
co2_avoided = 10.5 * T_fallback

ax1.plot(T_fallback, co2_avoided, marker="o", markersize=6, color="#55a868", linewidth=2.2)
for t, val in zip(T_fallback, co2_avoided):
    ax1.annotate(f"{val:.0f}", xy=(t, val), xytext=(0, 6), textcoords="offset points",
                 ha="center", va="bottom", fontsize=8.5)

ax1.set_xlabel("Assumed manual-restoration fallback delay (minutes)")
ax1.set_ylabel(r"Estimated $\mathrm{CO}_2$ avoided per storm event (kg)")
ax1.set_title(r"(b) Emissions avoided vs. fallback delay", fontweight="bold")
ax1.set_xticks(np.arange(20, 100, 10))
ax1.set_xlim(10, 96)
ax1.set_ylim(100, 1050)
ax1.grid(True, linestyle=":", alpha=0.35)

plt.tight_layout()

# Save to Review/figures
out_pdf = "figures/fig16_exp10_emissions.pdf"
out_png = "figures/fig16_exp10_emissions.png"
plt.savefig(out_pdf)
plt.savefig(out_png, dpi=300)
plt.close()
print("Saved fig16_exp10_emissions successfully.")
