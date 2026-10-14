"""
ChemSafePlot - Chemical Engineering Plant Layout & Safety Siting Auditor
Author: Chemical Process Safety Systems
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches
import numpy as np

from safety_standards import (
    EQUIPMENT_TYPES,
    Equipment,
    SafetyAuditor,
    SafetyViolation,
    WindHazardWarning
)
from sample_layouts import HAZARDOUS_REFINERY_LAYOUT, COMPLIANT_PLANT_LAYOUT

class ChemSafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChemSafePlot - Chemical Plant Layout & Safety Siting Auditor")
        self.root.geometry("1400x850")
        self.root.state('zoomed')  # Maximize on Windows

        self.equipment_list = [Equipment(**eq.__dict__) for eq in HAZARDOUS_REFINERY_LAYOUT]
        self.wind_angle = 45.0
        self.auditor = SafetyAuditor(self.wind_angle)
        self.dragging_eq = None

        self._setup_style()
        self._create_layout()
        self.run_audit_and_plot()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#F5F7FA")
        style.configure("TLabel", background="#F5F7FA", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1A237E")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)
        style.configure("Action.TButton", background="#1565C0", foreground="white")
        style.map("Action.TButton", background=[("active", "#0D47A1")])

    def _create_layout(self):
        # Main Paned window (Left: Map, Right: Control & Audit)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left Frame: Plot Canvas
        map_frame = ttk.Frame(main_paned)
        main_paned.add(map_frame, weight=3)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(8, 7), dpi=100)
        self.fig.patch.set_facecolor('#FFFFFF')
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = ttk.Frame(map_frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Canvas drag-and-drop bindings
        self.canvas.mpl_connect("button_press_event", self._on_canvas_click)
        self.canvas.mpl_connect("button_release_event", self._on_canvas_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_canvas_motion)

        # Right Frame: Controls & Audit Results
        side_frame = ttk.Frame(main_paned)
        main_paned.add(side_frame, weight=2)

        # Control Panel Card
        control_card = ttk.LabelFrame(side_frame, text=" Scenario & Control Tools ", padding=10)
        control_card.pack(fill=tk.X, pady=(0, 6))

        btn_row1 = ttk.Frame(control_card)
        btn_row1.pack(fill=tk.X, pady=2)
        ttk.Button(btn_row1, text="Load Hazardous Refinery (Test Deficiencies)", command=self.load_hazardous_sample).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_row1, text="Load Compliant Plant (Optimized)", command=self.load_compliant_sample).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

        btn_row2 = ttk.Frame(control_card)
        btn_row2.pack(fill=tk.X, pady=4)
        ttk.Button(btn_row2, text="Re-run Safety Audit", style="Action.TButton", command=self.run_audit_and_plot).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_row2, text="Export Comprehensive Report", command=self.export_report).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

        # Wind Direction Control
        wind_frame = ttk.Frame(control_card)
        wind_frame.pack(fill=tk.X, pady=4)
        ttk.Label(wind_frame, text="Prevailing Wind Angle:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.wind_slider = ttk.Scale(wind_frame, from_=0, to=360, value=self.wind_angle, command=self._on_wind_change)
        self.wind_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.wind_lbl = ttk.Label(wind_frame, text=f"{int(self.wind_angle)}°")
        self.wind_lbl.pack(side=tk.LEFT, padx=3)

        # Add Equipment Panel
        add_card = ttk.LabelFrame(side_frame, text=" Add New Process Equipment ", padding=6)
        add_card.pack(fill=tk.X, pady=(0, 6))

        add_grid = ttk.Frame(add_card)
        add_grid.pack(fill=tk.X)

        ttk.Label(add_grid, text="Type:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.add_type_var = tk.StringVar(value="FIRED_HEATER")
        type_combo = ttk.Combobox(add_grid, textvariable=self.add_type_var, values=list(EQUIPMENT_TYPES.keys()), state="readonly", width=18)
        type_combo.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(add_grid, text="Name:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.add_name_var = tk.StringVar(value="New Equipment")
        ttk.Entry(add_grid, textvariable=self.add_name_var, width=15).grid(row=0, column=3, padx=2, pady=2)

        ttk.Label(add_grid, text="Coord X (m):").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.add_x_var = tk.DoubleVar(value=100.0)
        ttk.Entry(add_grid, textvariable=self.add_x_var, width=8).grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)

        ttk.Label(add_grid, text="Coord Y (m):").grid(row=1, column=2, sticky=tk.W, padx=2)
        self.add_y_var = tk.DoubleVar(value=100.0)
        ttk.Entry(add_grid, textvariable=self.add_y_var, width=8).grid(row=1, column=3, sticky=tk.W, padx=2, pady=2)

        ttk.Button(add_card, text="+ Insert Equipment to Plot Plan", command=self.add_custom_equipment).pack(fill=tk.X, pady=3)

        # KPI Summary Dashboard
        self.kpi_frame = ttk.Frame(side_frame)
        self.kpi_frame.pack(fill=tk.X, pady=(0, 6))

        self.kpi_total = self._create_kpi_box(self.kpi_frame, "Total Equipment", "0", "#2196F3")
        self.kpi_crit = self._create_kpi_box(self.kpi_frame, "Critical Violations", "0", "#D32F2F")
        self.kpi_warn = self._create_kpi_box(self.kpi_frame, "Spacing Warnings", "0", "#FF9800")
        self.kpi_wind = self._create_kpi_box(self.kpi_frame, "Wind Hazard Flags", "0", "#7B1FA2")

        # Audit Report Table (Notebook with tabs)
        tabs = ttk.Notebook(side_frame)
        tabs.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Spacing Violations
        tab_viol = ttk.Frame(tabs)
        tabs.add(tab_viol, text=" Separation Distance Violations ")

        cols = ("eq1", "eq2", "actual", "required", "deficit", "severity", "standard")
        self.tree_viol = ttk.Treeview(tab_viol, columns=cols, show="headings", height=8)
        self.tree_viol.heading("eq1", text="Unit A")
        self.tree_viol.heading("eq2", text="Unit B")
        self.tree_viol.heading("actual", text="Actual (m)")
        self.tree_viol.heading("required", text="Standard (m)")
        self.tree_viol.heading("deficit", text="Deficit (m)")
        self.tree_viol.heading("severity", text="Risk Severity")
        self.tree_viol.heading("standard", text="Standard Ref.")

        self.tree_viol.column("eq1", width=120)
        self.tree_viol.column("eq2", width=120)
        self.tree_viol.column("actual", width=75, anchor="center")
        self.tree_viol.column("required", width=80, anchor="center")
        self.tree_viol.column("deficit", width=75, anchor="center")
        self.tree_viol.column("severity", width=95, anchor="center")
        self.tree_viol.column("standard", width=145)

        tree_scroll_y = ttk.Scrollbar(tab_viol, orient=tk.VERTICAL, command=self.tree_viol.yview)
        self.tree_viol.configure(yscrollcommand=tree_scroll_y.set)
        self.tree_viol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_viol.bind("<<TreeviewSelect>>", self._on_violation_selected)

        # Tab 2: Wind Hazards
        tab_wind = ttk.Frame(tabs)
        tabs.add(tab_wind, text=" Atmospheric Wind Drift Hazards ")

        cols_w = ("source", "target", "hazard", "desc")
        self.tree_wind = ttk.Treeview(tab_wind, columns=cols_w, show="headings", height=8)
        self.tree_wind.heading("source", text="Release Source")
        self.tree_wind.heading("target", text="Impacted Asset")
        self.tree_wind.heading("hazard", text="Hazard Classification")
        self.tree_wind.heading("desc", text="Safety & Siting Rationale")

        self.tree_wind.column("source", width=120)
        self.tree_wind.column("target", width=120)
        self.tree_wind.column("hazard", width=160)
        self.tree_wind.column("desc", width=250)

        self.tree_wind.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_lbl = ttk.Label(side_frame, text="Ready. Click and drag any unit on the map to re-evaluate spacing.", font=("Segoe UI", 9, "italic"))
        self.status_lbl.pack(fill=tk.X, pady=4)

    def _create_kpi_box(self, parent, title, val, color):
        frame = tk.Frame(parent, bg=color, bd=1, relief=tk.RAISED)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        lbl_t = tk.Label(frame, text=title, fg="white", bg=color, font=("Segoe UI", 8, "bold"))
        lbl_t.pack(pady=(2, 0))
        lbl_v = tk.Label(frame, text=val, fg="white", bg=color, font=("Segoe UI", 13, "bold"))
        lbl_v.pack(pady=(0, 2))
        return lbl_v

    def _on_wind_change(self, val):
        self.wind_angle = float(val)
        self.wind_lbl.config(text=f"{int(self.wind_angle)}°")
        self.auditor = SafetyAuditor(self.wind_angle)
        self.run_audit_and_plot()

    def load_hazardous_sample(self):
        self.equipment_list = [Equipment(**eq.__dict__) for eq in HAZARDOUS_REFINERY_LAYOUT]
        self.run_audit_and_plot()
        self.status_lbl.config(text="Loaded high-hazard refinery layout with deliberate spacing violations.")

    def load_compliant_sample(self):
        self.equipment_list = [Equipment(**eq.__dict__) for eq in COMPLIANT_PLANT_LAYOUT]
        self.run_audit_and_plot()
        self.status_lbl.config(text="Loaded compliant and optimized plant layout.")

    def add_custom_equipment(self):
        eq_type = self.add_type_var.get()
        name = self.add_name_var.get()
        x = self.add_x_var.get()
        y = self.add_y_var.get()
        eq_id = f"EQ-{len(self.equipment_list) + 1:02d}"
        radius = EQUIPMENT_TYPES.get(eq_type, {}).get("default_radius", 6.0)

        new_eq = Equipment(id=eq_id, name=name, eq_type=eq_type, x=x, y=y, radius=radius)
        self.equipment_list.append(new_eq)
        self.run_audit_and_plot()
        self.status_lbl.config(text=f"Equipment '{name}' added to plot plan.")

    def run_audit_and_plot(self):
        violations, wind_warnings = self.auditor.audit_layout(self.equipment_list)
        self.current_violations = violations
        self.current_wind_warnings = wind_warnings

        # Update KPI values
        crit_count = sum(1 for v in violations if "CRITICAL" in v.severity)
        warn_count = sum(1 for v in violations if "CRITICAL" not in v.severity)
        self.kpi_total.config(text=str(len(self.equipment_list)))
        self.kpi_crit.config(text=str(crit_count))
        self.kpi_warn.config(text=str(warn_count))
        self.kpi_wind.config(text=str(len(wind_warnings)))

        # Populate Spacing Violations Table
        for item in self.tree_viol.get_children():
            self.tree_viol.delete(item)
        for v in violations:
            self.tree_viol.insert("", tk.END, values=(
                f"{v.eq1.name} ({v.eq1.id})",
                f"{v.eq2.name} ({v.eq2.id})",
                f"{v.actual_distance} m",
                f"{v.required_distance} m",
                f"-{v.deficit} m",
                v.severity,
                v.standard
            ))

        # Populate Wind Warnings Table
        for item in self.tree_wind.get_children():
            self.tree_wind.delete(item)
        for w in wind_warnings:
            self.tree_wind.insert("", tk.END, values=(
                w.source_eq.name,
                w.target_eq.name,
                w.hazard_type,
                w.explanation
            ))

        self._plot_map(violations)

    def _plot_map(self, violations):
        self.ax.clear()
        self.ax.set_facecolor("#FAFAFA")
        self.ax.set_title("Process Plant Plot Plan & Safety Siting Audit (CCPS / NFPA / API)", fontsize=11, fontweight="bold", pad=12)
        self.ax.set_xlabel("X Coordinate (Meters)", fontsize=9)
        self.ax.set_ylabel("Y Coordinate (Meters)", fontsize=9)
        self.ax.grid(True, linestyle="--", alpha=0.5)

        # Plot Wind Indicator Compass
        w_rad = np.radians(self.wind_angle)
        wx, wy = np.cos(w_rad), np.sin(w_rad)
        self.ax.annotate(
            "", xy=(25 + wx * 15, 200 + wy * 15), xytext=(25, 200),
            arrowprops=dict(facecolor="#283593", edgecolor="#1A237E", width=3, headwidth=9, alpha=0.85)
        )
        self.ax.text(25, 218, f"Prevailing Wind ({int(self.wind_angle)}°)", fontsize=8, fontweight="bold", color="#1A237E", ha="center")

        # Plot Red/Orange Violation Connection Lines
        for v in violations:
            is_crit = "CRITICAL" in v.severity
            line_col = "#D50000" if is_crit else "#FF6D00"
            line_width = 2.5 if is_crit else 1.8
            line_style = "-" if is_crit else "--"

            self.ax.plot(
                [v.eq1.x, v.eq2.x], [v.eq1.y, v.eq2.y],
                color=line_col, linestyle=line_style, linewidth=line_width, alpha=0.85, zorder=2
            )
            # Label actual vs required distance on midpoint
            mid_x = (v.eq1.x + v.eq2.x) / 2
            mid_y = (v.eq1.y + v.eq2.y) / 2
            self.ax.text(
                mid_x, mid_y, f"{v.actual_distance}m < {v.required_distance}m",
                fontsize=7.5, color="white", weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=line_col, edgecolor="none", alpha=0.85),
                ha="center", va="center", zorder=3
            )

        # Plot Equipment Footprints and Name Tags
        for eq in self.equipment_list:
            info = eq.info
            color = info.get("color", "#757575")

            # Hazard Buffer Circle
            hazard_circle = patches.Circle(
                (eq.x, eq.y), eq.radius,
                facecolor=color, edgecolor="#212121", linewidth=1.5, alpha=0.65, zorder=4
            )
            self.ax.add_patch(hazard_circle)

            # Center Point
            self.ax.plot(eq.x, eq.y, marker="o", markersize=4, color="white", zorder=5)

            # Label
            self.ax.text(
                eq.x, eq.y - eq.radius - 3, f"{eq.id}\n{eq.name}",
                fontsize=7.5, fontweight="bold", ha="center", va="top", color="#212121",
                bbox=dict(boxstyle="square,pad=0.15", facecolor="#FFFFFF", edgecolor="#BDBDBD", alpha=0.8),
                zorder=6
            )

        self.ax.set_xlim(0, 220)
        self.ax.set_ylim(0, 220)
        self.canvas.draw()

    # Dragging logic on Matplotlib Canvas
    def _on_canvas_click(self, event):
        if event.inaxes != self.ax:
            return
        click_x, click_y = event.xdata, event.ydata
        for eq in self.equipment_list:
            dist = math.hypot(eq.x - click_x, eq.y - click_y)
            if dist <= eq.radius + 3:
                self.dragging_eq = eq
                self.status_lbl.config(text=f"Repositioning equipment: {eq.name} ({eq.id})")
                break

    def _on_canvas_release(self, event):
        if self.dragging_eq:
            self.dragging_eq = None
            self.run_audit_and_plot()
            self.status_lbl.config(text="Equipment position updated. Safety audit recalculated.")

    def _on_canvas_motion(self, event):
        if self.dragging_eq and event.inaxes == self.ax:
            self.dragging_eq.x = round(event.xdata, 1)
            self.dragging_eq.y = round(event.ydata, 1)
            self.run_audit_and_plot()

    def _on_violation_selected(self, event):
        selected_item = self.tree_viol.focus()
        if not selected_item:
            return
        vals = self.tree_viol.item(selected_item, "values")
        if vals and len(vals) >= 2:
            eq1_str = vals[0]
            eq2_str = vals[1]
            for v in self.current_violations:
                if f"{v.eq1.name} ({v.eq1.id})" == eq1_str and f"{v.eq2.name} ({v.eq2.id})" == eq2_str:
                    messagebox.showwarning(
                        "Chemical Process Safety Evaluation",
                        f"SEVERITY: {v.severity}\n\n"
                        f"Units: {v.eq1.name} & {v.eq2.name}\n"
                        f"Actual Separation: {v.actual_distance} m | Minimum Required: {v.required_distance} m\n"
                        f"Deficit: {v.deficit} m\n"
                        f"Standard Reference: {v.standard}\n\n"
                        f"Chemical Engineering Hazard Rationale:\n{v.explanation}\n\n"
                        f"Recommended Mitigation:\nIncrease physical buffer distance or install heavy-duty blast wall with continuous flammable gas sensors."
                    )
                    break

    def export_report(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Report", "*.html"), ("Text Report", "*.txt")]
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chemical Plant Layout Safety Audit Report</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; background: #f4f6f8; padding: 25px; line-height: 1.6; color: #333; }}
h1, h2 {{ color: #1a237e; }}
.card {{ background: white; padding: 18px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
th, td {{ border: 1px solid #e0e0e0; padding: 10px; text-align: left; }}
th {{ background: #1565c0; color: white; }}
.crit {{ color: #d32f2f; font-weight: bold; }}
.warn {{ color: #f57c00; font-weight: bold; }}
</style>
</head>
<body>
<h1>Plant Layout & Siting Safety Audit Report</h1>
<div class="card">
<p><strong>Total Equipment Units:</strong> {len(self.equipment_list)}</p>
<p><strong>Critical Spacing Violations:</strong> {sum(1 for v in self.current_violations if 'CRITICAL' in v.severity)}</p>
<p><strong>Prevailing Wind Direction:</strong> {self.wind_angle}°</p>
</div>

<div class="card">
<h2>Separation Distance Non-Compliance (NFPA 30 / CCPS / API 521 / API 752)</h2>
<table>
<tr>
<th>Unit A</th><th>Unit B</th><th>Actual Dist</th><th>Required Dist</th><th>Deficit</th><th>Severity</th><th>Standard Reference</th><th>Engineering Rationale</th>
</tr>
""")
            for v in self.current_violations:
                cls = "crit" if "CRITICAL" in v.severity else "warn"
                f.write(f"""<tr>
<td>{v.eq1.name}</td>
<td>{v.eq2.name}</td>
<td>{v.actual_distance} m</td>
<td>{v.required_distance} m</td>
<td>-{v.deficit} m</td>
<td class="{cls}">{v.severity}</td>
<td>{v.standard}</td>
<td>{v.explanation}</td>
</tr>""")

            f.write("""</table></div>
<div class="card">
<h2>Prevailing Atmospheric Wind Hazards</h2>
<ul>""")
            for w in self.current_wind_warnings:
                f.write(f"<li><strong>{w.hazard_type}:</strong> {w.explanation}</li>")

            f.write("""</ul></div></body></html>""")

        messagebox.showinfo("Export Successful", f"Audit report successfully exported to:\n{filepath}")

def main():
    root = tk.Tk()
    app = ChemSafeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
