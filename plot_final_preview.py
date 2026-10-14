"""
Generate a complete, high-resolution annotated image of the audited plant layout
File: FINAL_PLOT_PLAN_AUDIT.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import safety_standards

def generate_visual_audit():
    # 1. Run safety audit
    verifier = safety_standards.AntiGravityLayoutVerifier(prevailing_wind_deg=45.0)
    verifier.import_from_csv("sample_plot_plan_coordinates.csv")
    violations = verifier.verify_fire_zones()
    wind_hazards = verifier.verify_wind_orientation()

    # 2. Setup figure with dark engineering theme
    fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
    fig.patch.set_facecolor('#0b1120')
    ax.set_facecolor('#070d17')

    map_dim = 220
    ax.set_xlim(0, map_dim)
    ax.set_ylim(0, map_dim)
    ax.set_aspect('equal')

    # Load Blueprint background if exists
    try:
        import matplotlib.image as mpimg
        bg = mpimg.imread("sample_refinery_blueprint.png")
        ax.imshow(bg, extent=[0, map_dim, 0, map_dim], alpha=0.55, zorder=1)
    except Exception as e:
        print("Blueprint load note:", e)

    # Grid
    ax.grid(True, which='both', color='#1e293b', linestyle='--', linewidth=0.8, alpha=0.6, zorder=2)

    # Wind Arrow Indicator in corner
    w_rad = np.radians(45.0)
    wx, wy = np.cos(w_rad), np.sin(w_rad)
    ax.annotate(
        "", xy=(30 + wx * 18, 195 + wy * 18), xytext=(30, 195),
        arrowprops=dict(facecolor="#38bdf8", edgecolor="#0284c7", width=3, headwidth=9),
        zorder=10
    )
    ax.text(30, 185, "Prevailing Wind (45° NE)\n[IPS-E-PR-190 Siting Vector]", color='#38bdf8', fontsize=8.5, fontweight='bold', ha='center', zorder=10)

    # Plot Non-Compliance Red/Orange Lines
    for v in violations:
        is_crit = v.severity == "CRITICAL"
        line_color = '#ef4444' if is_crit else '#f59e0b'
        line_style = '-' if is_crit else '--'
        lw = 2.5 if is_crit else 1.8

        ax.plot([v.node1.coord_x, v.node2.coord_x], [v.node1.coord_y, v.node2.coord_y],
                color=line_color, linestyle=line_style, linewidth=lw, alpha=0.85, zorder=4)

        # Distance badge at midpoint
        mid_x = (v.node1.coord_x + v.node2.coord_x) / 2
        mid_y = (v.node1.coord_y + v.node2.coord_y) / 2
        ax.text(mid_x, mid_y, f"{v.actual_distance}m < {v.required_distance}m\n(Deficit: -{v.deficit}m)",
                color='white', fontsize=7.5, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.25', facecolor=line_color, edgecolor='none', alpha=0.9),
                zorder=6)

    # Plot Equipment Nodes with Hazard Radii
    for node in verifier.nodes:
        meta = safety_standards.CATEGORY_META.get(node.category, {})
        color = meta.get('color', '#38bdf8')
        radius = node.radius

        # Hazard Buffer Circle
        circle = patches.Circle((node.coord_x, node.coord_y), radius,
                                facecolor=color, edgecolor='#ffffff', linewidth=1.5, alpha=0.45, zorder=5)
        ax.add_patch(circle)

        # Center Marker
        ax.plot(node.coord_x, node.coord_y, marker='o', markersize=5, color='white', zorder=7)

        # Label Tag
        ax.text(node.coord_x, node.coord_y - radius - 3.5, f"{node.tag}\n{meta.get('name_en', node.category.value)[:16]}",
                color='#f8fafc', fontsize=7.5, fontweight='bold', ha='center', va='top',
                bbox=dict(boxstyle='square,pad=0.2', facecolor='#0f172a', edgecolor=color, linewidth=1, alpha=0.9),
                zorder=8)

    # Header Title Banner
    title_box = patches.Rectangle((45, 204), 130, 14, facecolor='#0f172a', edgecolor='#38bdf8', linewidth=1.5, zorder=10)
    ax.add_patch(title_box)
    ax.text(110, 211, "FACILITY SITING AUDIT: IPS-G-SF-150 / INSO 23591 & TotalEnergies",
            color='#38bdf8', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=11)

    # KPI Summary Box at bottom right
    kpi_box = patches.Rectangle((120, 8), 95, 22, facecolor='#0f172a', edgecolor='#334155', linewidth=1.2, zorder=10)
    ax.add_patch(kpi_box)
    ax.text(125, 22, f"Total Units: {len(verifier.nodes)} | Critical Siting Gaps: {sum(1 for v in violations if v.severity=='CRITICAL')}", color='#f8fafc', fontsize=7.5, fontweight='bold', zorder=11)
    ax.text(125, 14, f"Fire Separation Deficiencies: {len(violations)} | Wind Hazards: {len(wind_hazards)}", color='#ef4444', fontsize=7.5, fontweight='bold', zorder=11)

    plt.tight_layout()
    out_img = "FINAL_PLOT_PLAN_AUDIT.png"
    plt.savefig(out_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Saved visual audit:", out_img)

if __name__ == "__main__":
    generate_visual_audit()
