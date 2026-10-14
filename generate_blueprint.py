"""
Script to generate a realistic Chemical Plant / Refinery Plot Plan Blueprint
File: sample_refinery_blueprint.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_blueprint():
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor('#0f2038')
    ax.set_facecolor('#0d1b2a')

    # Dimensions: 220m x 220m
    ax.set_xlim(0, 220)
    ax.set_ylim(0, 220)
    ax.set_aspect('equal')

    # Grid
    ax.grid(True, which='both', color='#1b3a5c', linestyle='-', linewidth=0.8, alpha=0.7)

    # Perimeter Security Fence
    fence = patches.Rectangle((5, 5), 210, 210, linewidth=2, edgecolor='#415a77', facecolor='none', linestyle='--')
    ax.add_patch(fence)
    ax.text(10, 212, "SITE PERIMETER BOUNDARY (220m x 220m)", color='#778da9', fontsize=9, fontweight='bold', fontfamily='monospace')

    # Internal Plant Roads (Grayish blue asphalt corridors)
    roads = [
        # Main peripheral loop road
        patches.Rectangle((12, 12), 196, 12, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
        patches.Rectangle((12, 196), 196, 12, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
        patches.Rectangle((12, 12), 12, 196, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
        patches.Rectangle((196, 12), 12, 196, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
        # Central spine road
        patches.Rectangle((100, 12), 14, 196, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
        patches.Rectangle((12, 95), 196, 14, facecolor='#1b263b', edgecolor='#415a77', linewidth=1),
    ]
    for r in roads:
        ax.add_patch(r)

    # Road labels
    ax.text(107, 18, "MAIN ACCESS ROAD - GATE 1", color='#e0e1dd', fontsize=7, rotation=90, va='bottom', ha='center', fontfamily='monospace')
    ax.text(18, 102, "CROSS SPRAY ACCESS WAY", color='#e0e1dd', fontsize=7, va='center', fontfamily='monospace')

    # ZONE 1: Tank Farm & Dike Area (Bottom Right)
    dike = patches.Rectangle((125, 30), 65, 55, linewidth=2, edgecolor='#e63946', facecolor='#1b2838', linestyle='-')
    ax.add_patch(dike)
    ax.text(128, 80, "STORAGE DIKE BUND WALL (NFPA 30)", color='#e63946', fontsize=8, fontweight='bold', fontfamily='monospace')
    # Tanks footprints inside dike
    t1 = patches.Circle((145, 55), 10, facecolor='#27384e', edgecolor='#a855f7', linewidth=2)
    t2 = patches.Circle((172, 55), 10, facecolor='#27384e', edgecolor='#a855f7', linewidth=2)
    ax.add_patch(t1)
    ax.add_patch(t2)
    ax.text(145, 55, "TK-101\nLPG", color='#ffffff', fontsize=8, ha='center', va='center', fontweight='bold')
    ax.text(172, 55, "TK-102\nLPG", color='#ffffff', fontsize=8, ha='center', va='center', fontweight='bold')

    # ZONE 2: Primary Reaction & Cracking Unit (Center Left)
    process_block = patches.Rectangle((30, 115), 65, 75, linewidth=1.5, edgecolor='#f97316', facecolor='#1b2838')
    ax.add_patch(process_block)
    ax.text(35, 185, "BLOCK 100: HYDROTREATING & REACTION", color='#f97316', fontsize=8, fontweight='bold', fontfamily='monospace')
    # Reactor platform
    r1 = patches.Circle((55, 145), 7, facecolor='#27384e', edgecolor='#f97316', linewidth=2)
    ax.add_patch(r1)
    ax.text(55, 145, "R-301\nReactor", color='#ffffff', fontsize=7.5, ha='center', va='center', fontweight='bold')
    # Pipe Rack Corridor
    piperack = patches.Rectangle((32, 118), 61, 8, facecolor='#334155', edgecolor='#64748b', linewidth=1)
    ax.add_patch(piperack)
    ax.text(62, 122, "MAIN PIPE RACK CORRIDOR", color='#cbd5e1', fontsize=6.5, ha='center', va='center')

    # ZONE 3: Fired Heater / Cracking Furnace (Bottom Left)
    furnace_pad = patches.Rectangle((35, 35), 45, 50, linewidth=1.5, edgecolor='#ef4444', facecolor='#1b2838')
    ax.add_patch(furnace_pad)
    ax.text(38, 80, "CRACKING FURNACE FOUNDATION", color='#ef4444', fontsize=8, fontweight='bold', fontfamily='monospace')
    f1 = patches.Rectangle((45, 45), 20, 20, facecolor='#27384e', edgecolor='#ef4444', linewidth=2)
    ax.add_patch(f1)
    ax.text(55, 55, "FH-101\nFurnace", color='#ffffff', fontsize=8, ha='center', va='center', fontweight='bold')

    # ZONE 4: Administrative & Control Room Safe Zone (Top Left)
    admin_block = patches.Rectangle((30, 25), 55, 0) # empty
    cr_pad = patches.Rectangle((30, 198), 50, 18) # empty
    control_room = patches.Rectangle((30, 198), 0, 0)
    cr = patches.Rectangle((35, 198), 55, 15, facecolor='#1e3a8a', edgecolor='#3b82f6', linewidth=2)
    ax.add_patch(cr)
    ax.text(62, 205, "CENTRAL CONTROL & SUBSTATION (CR-01)", color='#ffffff', fontsize=7.5, ha='center', va='center', fontweight='bold')

    # ZONE 5: Flare Relief Area (Top Right)
    flare_area = patches.Circle((185, 185), 22, facecolor='none', edgecolor='#ec4899', linewidth=1.5, linestyle=':')
    ax.add_patch(flare_area)
    ax.plot(185, 185, marker='*', markersize=12, color='#ec4899')
    ax.text(185, 185, "\n\nFL-501\nFLARE", color='#ec4899', fontsize=8, ha='center', va='center', fontweight='bold')
    ax.text(185, 160, "FLARE EXCLUSION ZONE (API 521)", color='#ec4899', fontsize=7, ha='center', fontfamily='monospace')

    # ZONE 6: Logistics & Road Tanker Gantry (Center Right)
    loading_gantry = patches.Rectangle((125, 120), 60, 35, facecolor='#134e4a', edgecolor='#14b8a6', linewidth=1.5)
    ax.add_patch(loading_gantry)
    ax.text(155, 137, "TANKER LOADING RACKS (LR-601)\n4 BAYS UNLOADING", color='#ffffff', fontsize=7.5, ha='center', va='center', fontweight='bold')

    # Title Block (Bottom Right Engineering Sheet border)
    title_box = patches.Rectangle((115, 196), 90, 18, facecolor='#0f172a', edgecolor='#38bdf8', linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(160, 208, "PETROCHEMICAL COMPLEX PLOT PLAN", color='#38bdf8', fontsize=8.5, fontweight='bold', ha='center', fontfamily='sans-serif')
    ax.text(160, 201, "DWG NO: ACC-PLT-2026-001 | SCALE: 1:1000", color='#94a3b8', fontsize=7, ha='center', fontfamily='monospace')

    # North / Wind Arrow
    ax.annotate("N", xy=(15, 185), xytext=(15, 175),
                arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=2, headwidth=7),
                color='#38bdf8', fontsize=10, fontweight='bold', ha='center')

    plt.tight_layout()
    output_path = "d:\\ACCERO\\chemical_safety_layout\\sample_refinery_blueprint.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Blueprint generated: {output_path}")

if __name__ == "__main__":
    generate_blueprint()
