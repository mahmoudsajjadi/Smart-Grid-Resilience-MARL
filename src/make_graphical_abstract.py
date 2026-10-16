import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

# Set clean aesthetic font
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

# 16:9 canvas (16 x 9 inches at 300 dpi)
fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis('off')

# Soft modern slate background
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#F8FAFC')

# ----------------- MAIN TITLE & HEADER -----------------
# Main Title Banner with increased font size
tbox = patches.FancyBboxPatch((0.55, 7.92), 14.9, 0.85, boxstyle="round,pad=0.06,rounding_size=0.15",
                              edgecolor='#1E3A8A', facecolor='#1E3A8A', zorder=2)
ax.add_patch(tbox)
ax.text(8.0, 8.35, "Sustainable Smart Grid Resilience and Renewable Integration",
        color='white', fontsize=21.0, fontweight='bold', ha='center', va='center', zorder=3)

# Subtitle Pill
sbox = patches.FancyBboxPatch((1.8, 7.35), 12.4, 0.42, boxstyle="round,pad=0.05,rounding_size=0.1",
                              edgecolor='#0D9488', facecolor='#CCFBF1', zorder=2)
ax.add_patch(sbox)
ax.text(8.0, 7.56, "Two-Tier Multi-Agent Framework: Fast Contextual Bandit Switching + Coordinated BESS & Volt–VAr Control",
        color='#0F766E', fontsize=11.2, fontweight='bold', ha='center', va='center', zorder=3)

# ----------------- 3 MAIN CARDS LAYOUT -----------------
card_y = 0.50
card_h = 6.65
col_w = 4.65

x1 = 0.55
x2 = 5.67
x3 = 10.80

head_h = 0.72

# ----------------- ICON DRAWING HELPERS -----------------
def draw_badge(ax, cx, cy, r, bg_col):
    badge = patches.Circle((cx, cy), r, facecolor=bg_col, edgecolor='none', zorder=5)
    ax.add_patch(badge)

def icon_lightning(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#FEE2E2')
    s = r * 0.72
    verts = [
        (cx - 0.1*s, cy + 0.85*s),
        (cx - 0.5*s, cy - 0.05*s),
        (cx - 0.05*s, cy - 0.05*s),
        (cx - 0.35*s, cy - 0.85*s),
        (cx + 0.5*s, cy + 0.1*s),
        (cx + 0.05*s, cy + 0.1*s)
    ]
    ax.add_patch(patches.Polygon(verts, closed=True, facecolor='#DC2626', edgecolor='#DC2626', zorder=6))

def icon_signal(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#FEF3C7')
    col = '#D97706'
    s = r * 0.7
    ax.plot([cx, cx], [cy - 0.7*s, cy + 0.1*s], color=col, lw=2.4, zorder=6)
    ax.plot([cx - 0.4*s, cx + 0.4*s], [cy - 0.7*s, cy - 0.7*s], color=col, lw=2.4, zorder=6)
    ax.add_patch(patches.Circle((cx, cy + 0.1*s), 0.13*s, facecolor=col, edgecolor='none', zorder=7))
    ax.add_patch(patches.Arc((cx, cy + 0.1*s), 0.8*s, 0.8*s, angle=0, theta1=35, theta2=145, color=col, lw=2.2, zorder=6))
    ax.add_patch(patches.Arc((cx, cy + 0.1*s), 1.35*s, 1.35*s, angle=0, theta1=35, theta2=145, color=col, lw=2.2, zorder=6))

def icon_sun(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#FEF9C3')
    col = '#EAB308'
    s = r * 0.7
    ax.add_patch(patches.Circle((cx, cy), 0.34*s, facecolor=col, edgecolor='none', zorder=6))
    for ang in np.linspace(0, 2*np.pi, 8, endpoint=False):
        ax.plot([cx + 0.5*s*np.cos(ang), cx + 0.78*s*np.cos(ang)],
                [cy + 0.5*s*np.sin(ang), cy + 0.78*s*np.sin(ang)],
                color=col, lw=2.2, solid_capstyle='round', zorder=6)

def icon_timer(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#FEE2E2')
    col = '#B91C1C'
    s = r * 0.7
    ax.add_patch(patches.Circle((cx, cy - 0.05*s), 0.6*s, facecolor='none', edgecolor=col, lw=2.2, zorder=6))
    ax.plot([cx, cx], [cy + 0.55*s, cy + 0.72*s], color=col, lw=2.4, zorder=6)
    ax.plot([cx - 0.2*s, cx + 0.2*s], [cy + 0.72*s, cy + 0.72*s], color=col, lw=2.4, zorder=6)
    ax.plot([cx, cx], [cy - 0.05*s, cy + 0.3*s], color=col, lw=2.2, zorder=6)
    ax.plot([cx, cx + 0.28*s], [cy - 0.05*s, cy - 0.05*s], color=col, lw=2.2, zorder=6)

def icon_switch(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#DBEAFE')
    col = '#2563EB'
    s = r * 0.7
    ax.add_patch(patches.Circle((cx - 0.42*s, cy - 0.12*s), 0.12*s, facecolor=col, edgecolor='none', zorder=6))
    ax.add_patch(patches.Circle((cx + 0.42*s, cy - 0.12*s), 0.12*s, facecolor=col, edgecolor='none', zorder=6))
    ax.plot([cx - 0.42*s, cx + 0.2*s], [cy - 0.12*s, cy + 0.45*s], color=col, lw=2.8, solid_capstyle='round', zorder=6)
    ax.plot([cx - 0.7*s, cx - 0.42*s], [cy - 0.12*s, cy - 0.12*s], color=col, lw=2.2, zorder=6)
    ax.plot([cx + 0.42*s, cx + 0.7*s], [cy - 0.12*s, cy - 0.12*s], color=col, lw=2.2, zorder=6)

def icon_battery(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#D1FAE5')
    col = '#059669'
    s = r * 0.7
    ax.add_patch(patches.FancyBboxPatch((cx - 0.34*s, cy - 0.55*s), 0.68*s, 0.98*s,
                                        boxstyle='round,pad=0.03,rounding_size=0.1',
                                        edgecolor=col, facecolor='white', lw=2.2, zorder=6))
    ax.add_patch(patches.Rectangle((cx - 0.15*s, cy + 0.45*s), 0.3*s, 0.13*s, facecolor=col, edgecolor='none', zorder=6))
    ax.add_patch(patches.Rectangle((cx - 0.24*s, cy - 0.45*s), 0.48*s, 0.68*s, facecolor=col, edgecolor='none', zorder=7))

def icon_network(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#EDE9FE')
    col = '#7C3AED'
    s = r * 0.7
    pts = [(cx, cy + 0.45*s), (cx - 0.45*s, cy - 0.35*s), (cx + 0.45*s, cy - 0.35*s)]
    for p in pts:
        ax.plot([cx, p[0]], [cy - 0.05*s, p[1]], color=col, lw=2.0, zorder=6)
    ax.add_patch(patches.Circle((cx, cy - 0.05*s), 0.18*s, facecolor=col, edgecolor='none', zorder=7))
    for p in pts:
        ax.add_patch(patches.Circle(p, 0.14*s, facecolor=col, edgecolor='none', zorder=7))

def icon_wave(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#CFFAFE')
    col = '#0891B2'
    s = r * 0.7
    x = np.linspace(cx - 0.6*s, cx + 0.6*s, 100)
    y = cy + 0.4*s * np.sin(2 * np.pi * (x - cx) / (1.0*s))
    ax.plot(x, y, color=col, lw=2.8, solid_capstyle='round', zorder=6)
    ax.plot([cx - 0.7*s, cx + 0.7*s], [cy, cy], color=col, lw=1.2, linestyle=':', alpha=0.6, zorder=5)

def icon_chart(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#D1FAE5')
    col = '#059669'
    s = r * 0.7
    ax.plot([cx - 0.55*s, cx - 0.55*s, cx + 0.55*s], [cy + 0.55*s, cy - 0.55*s, cy - 0.55*s], color=col, lw=2.0, zorder=6)
    ax.plot([cx - 0.5*s, cx - 0.15*s, cx + 0.15*s, cx + 0.5*s],
            [cy - 0.35*s, cy - 0.1*s, cy + 0.15*s, cy + 0.5*s], color=col, lw=2.6, zorder=6)
    ax.plot([cx + 0.3*s, cx + 0.5*s, cx + 0.5*s], [cy + 0.5*s, cy + 0.5*s, cy + 0.3*s], color=col, lw=2.6, solid_capstyle='round', zorder=6)

def icon_speed(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#D1FAE5')
    col = '#047857'
    s = r * 0.7
    ax.add_patch(patches.Arc((cx, cy - 0.15*s), 1.1*s, 1.1*s, angle=0, theta1=0, theta2=180, color=col, lw=2.2, zorder=6))
    ax.plot([cx, cx + 0.3*s], [cy - 0.15*s, cy + 0.28*s], color='#DC2626', lw=2.5, solid_capstyle='round', zorder=7)
    ax.add_patch(patches.Circle((cx, cy - 0.15*s), 0.1*s, facecolor=col, edgecolor='none', zorder=8))

def icon_shield(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#D1FAE5')
    col = '#059669'
    s = r * 0.7
    verts = [
        (cx, cy + 0.6*s), (cx + 0.5*s, cy + 0.35*s), (cx + 0.45*s, cy - 0.2*s),
        (cx, cy - 0.65*s), (cx - 0.45*s, cy - 0.2*s), (cx - 0.5*s, cy + 0.35*s)
    ]
    ax.add_patch(patches.Polygon(verts, closed=True, facecolor='white', edgecolor=col, lw=2.2, zorder=6))
    ax.plot([cx - 0.22*s, cx - 0.05*s, cx + 0.25*s], [cy - 0.05*s, cy - 0.22*s, cy + 0.18*s], color=col, lw=2.5, solid_capstyle='round', zorder=7)

def icon_leaf(ax, cx, cy, r):
    draw_badge(ax, cx, cy, r, '#D1FAE5')
    col = '#047857'
    s = r * 0.7
    verts = [
        (cx - 0.45*s, cy - 0.45*s),
        (cx - 0.55*s, cy + 0.35*s), (cx + 0.45*s, cy + 0.45*s),
        (cx + 0.35*s, cy - 0.55*s), (cx - 0.45*s, cy - 0.45*s)
    ]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3]
    path = Path(verts, codes)
    ax.add_patch(patches.PathPatch(path, facecolor=col, edgecolor=col, lw=1.0, zorder=6))
    ax.plot([cx - 0.45*s, cx + 0.45*s], [cy - 0.45*s, cy + 0.45*s], color='#D1FAE5', lw=2.0, zorder=7)
    ax.plot([cx - 0.1*s, cx + 0.05*s], [cy - 0.1*s, cy + 0.15*s], color='#D1FAE5', lw=1.4, zorder=7)
    ax.plot([cx + 0.1*s, cx + 0.25*s], [cy + 0.1*s, cy + 0.3*s], color='#D1FAE5', lw=1.4, zorder=7)

# ----------------- GEOMETRY CALCULATIONS -----------------
box_h = 1.22
box_w = col_w - 0.28
badge_r = 0.36

gap = 0.23
top_edge = card_y + card_h - head_h - 0.16
y_bottoms = [top_edge - (i + 1) * box_h - i * gap for i in range(4)]

# ----------------- BUILD COLUMN 1 -----------------
c1 = patches.FancyBboxPatch((x1, card_y), col_w, card_h, boxstyle="round,pad=0.08,rounding_size=0.15",
                            edgecolor='#E2E8F0', facecolor='white', linewidth=1.5, zorder=2)
ax.add_patch(c1)
h1 = patches.FancyBboxPatch((x1, card_y + card_h - head_h), col_w, head_h, boxstyle="round,pad=0.05,rounding_size=0.1",
                            edgecolor='#DC2626', facecolor='#FEE2E2', zorder=3)
ax.add_patch(h1)
ax.text(x1 + col_w/2, card_y + card_h - head_h/2, "1. GRID EMERGENCIES", color='#991B1B', fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=4)

items1 = [
    ("Severe Weather & Line Outages",
     "Simultaneous N-1 & N-2 line faults across\nIEEE 33-bus and 179-bus networks",
     icon_lightning),
    ("Cyber Communication Loss",
     "Inter-agent packet loss & correlated 2-state\nGilbert–Elliott burst packet loss",
     icon_signal),
    ("Renewable Voltage Excursions",
     "Severe overvoltage (>1.10 p.u.) from high solar\npenetration without inverter reactive support",
     icon_sun),
    ("Fast Protection Deadlines",
     "Must reconfigure within 300–500 ms recloser\ndead time to avoid lockout & diesel fallback",
     icon_timer)
]

for i, (title, desc, icon_func) in enumerate(items1):
    by = y_bottoms[i]
    bx = x1 + 0.14
    pbox = patches.FancyBboxPatch((bx, by), box_w, box_h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                  edgecolor='#E2E8F0', facecolor='#F8FAFC', zorder=3)
    ax.add_patch(pbox)
    
    # Icon badge
    icx = bx + 0.50
    icy = by + box_h / 2
    icon_func(ax, icx, icy, badge_r)
    
    # Text
    tx = bx + 1.05
    ax.text(tx, by + 0.82, title, fontsize=11.2, fontweight='bold', color='#0F172A', va='center', zorder=4)
    ax.text(tx, by + 0.38, desc, fontsize=9.4, color='#475569', va='center', linespacing=1.28, zorder=4)

# ----------------- BUILD COLUMN 2 -----------------
c2 = patches.FancyBboxPatch((x2, card_y), col_w, card_h, boxstyle="round,pad=0.08,rounding_size=0.15",
                            edgecolor='#3B82F6', facecolor='white', linewidth=2, zorder=2)
ax.add_patch(c2)
h2 = patches.FancyBboxPatch((x2, card_y + card_h - head_h), col_w, head_h, boxstyle="round,pad=0.05,rounding_size=0.1",
                            edgecolor='#2563EB', facecolor='#DBEAFE', zorder=3)
ax.add_patch(h2)
ax.text(x2 + col_w/2, card_y + card_h - head_h/2, "2. DECENTRALIZED MULTI-AGENT", color='#1D4ED8', fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=4)

items2 = [
    ("Tier 1: Emergency Switching",
     "Contextual bandit (T=1, γ=0) with instant\nQ-lookup (<100 ms) & radial AC validation",
     icon_switch),
    ("Tier 2: Coordinated BESS",
     "Sequential 24-h MDP battery coordination\npooling storage for critical load facilities",
     icon_battery),
    ("ComDML Edge Acceleration",
     "Workload-balanced decentralized learning;\n1.46× faster training, zero straggler delay",
     icon_network),
    ("Autonomous Volt–VAr Droop",
     "Local IEEE 1547 reactive power control\nabsorbing VArs with zero communication",
     icon_wave)
]

for i, (title, desc, icon_func) in enumerate(items2):
    by = y_bottoms[i]
    bx = x2 + 0.14
    pbox = patches.FancyBboxPatch((bx, by), box_w, box_h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                  edgecolor='#BFDBFE', facecolor='#EFF6FF', zorder=3)
    ax.add_patch(pbox)
    
    # Icon badge
    icx = bx + 0.50
    icy = by + box_h / 2
    icon_func(ax, icx, icy, badge_r)
    
    # Text
    tx = bx + 1.05
    ax.text(tx, by + 0.82, title, fontsize=11.2, fontweight='bold', color='#0F172A', va='center', zorder=4)
    ax.text(tx, by + 0.38, desc, fontsize=9.4, color='#334155', va='center', linespacing=1.28, zorder=4)

# ----------------- BUILD COLUMN 3 -----------------
c3 = patches.FancyBboxPatch((x3, card_y), col_w, card_h, boxstyle="round,pad=0.08,rounding_size=0.15",
                            edgecolor='#10B981', facecolor='white', linewidth=1.5, zorder=2)
ax.add_patch(c3)
h3 = patches.FancyBboxPatch((x3, card_y + card_h - head_h), col_w, head_h, boxstyle="round,pad=0.05,rounding_size=0.1",
                            edgecolor='#059669', facecolor='#D1FAE5', zorder=3)
ax.add_patch(h3)
ax.text(x3 + col_w/2, card_y + card_h - head_h/2, "3. SUSTAINABILITY & IMPACT", color='#047857', fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=4)

items3 = [
    ("+51% PV Hosting Capacity",
     "Elevates solar from 7.29 to 11.01 MW\n(296% peak) with zero curtailment",
     icon_chart),
    ("<100 ms Speed (72.7% Savings)",
     "Decentralized search meets recloser deadline;\ncentralized search fails (>940 ms on 33-bus)",
     icon_speed),
    ("97% Parity on Complete N-2",
     "1.53% optimality gap across all 496 line pairs;\nretains 34.4% restoration under cyber loss",
     icon_shield),
    ("158 – 945 kg Avoided CO$_2$",
     "Displaces diesel emergency backup runtime\nper storm; advances UN SDG 7 & SDG 13",
     icon_leaf)
]

for i, (title, desc, icon_func) in enumerate(items3):
    by = y_bottoms[i]
    bx = x3 + 0.14
    pbox = patches.FancyBboxPatch((bx, by), box_w, box_h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                  edgecolor='#A7F3D0', facecolor='#ECFDF5', zorder=3)
    ax.add_patch(pbox)
    
    # Icon badge
    icx = bx + 0.50
    icy = by + box_h / 2
    icon_func(ax, icx, icy, badge_r)
    
    # Text
    tx = bx + 1.05
    ax.text(tx, by + 0.82, title, fontsize=11.2, fontweight='bold', color='#064E3B', va='center', zorder=4)
    ax.text(tx, by + 0.38, desc, fontsize=9.4, color='#065F46', va='center', linespacing=1.28, zorder=4)

# ----------------- CLEAN BRIDGING ARROWS -----------------
arr1 = patches.FancyArrowPatch((x1 + col_w + 0.08, card_y + card_h - head_h/2),
                               (x2 - 0.08, card_y + card_h - head_h/2),
                               connectionstyle="arc3,rad=0",
                               arrowstyle="simple,head_width=11,head_length=13",
                               facecolor='#3B82F6', edgecolor='#1D4ED8', zorder=10)
ax.add_patch(arr1)

arr2 = patches.FancyArrowPatch((x2 + col_w + 0.08, card_y + card_h - head_h/2),
                               (x3 - 0.08, card_y + card_h - head_h/2),
                               connectionstyle="arc3,rad=0",
                               arrowstyle="simple,head_width=11,head_length=13",
                               facecolor='#10B981', edgecolor='#047857', zorder=10)
ax.add_patch(arr2)

# Footer caption
ax.text(8.0, 0.20, "Validated with full Newton–Raphson AC power flow on the IEEE 33-bus feeder and the synthetic 179-bus Oberrhein network",
        fontsize=10.2, color='#64748B', ha='center', va='center', style='italic')

plt.tight_layout()
plt.savefig('Final/graphical_abstract.png', dpi=300, bbox_inches='tight')
plt.savefig('Final/graphical_abstract.pdf', bbox_inches='tight')

# High resolution exports ending with high_res requested by MDPI editor
plt.savefig('Final/graphical_abstract_high_res.png', dpi=600, bbox_inches='tight')
plt.savefig('Final/graphical_abstract_high_res.tiff', dpi=600, bbox_inches='tight', pil_kwargs={'compression': 'tiff_lzw'})
plt.savefig('Final/graphical_abstract_high_res.jpg', dpi=600, bbox_inches='tight')
print("Successfully generated graphical abstract and high_res versions in Final/")

