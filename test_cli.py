"""
Quick CLI Test Runner for ChemSafePlot (English)
"""

import os
import sys

from safety_standards import SafetyAuditor
from sample_layouts import HAZARDOUS_REFINERY_LAYOUT, COMPLIANT_PLANT_LAYOUT

def run_test():
    print("=" * 75)
    print("[*] ChemSafePlot - Chemical Engineering Safety Siting Audit (CLI Test)")
    print("=" * 75)

    auditor = SafetyAuditor(wind_direction_deg=45.0)

    # 1. Audit Hazardous Refinery Layout
    print("\n[1] Auditing High-Hazard Refinery Plot Plan (Deficiency Detection)...")
    violations, wind_hazards = auditor.audit_layout(HAZARDOUS_REFINERY_LAYOUT)

    print(f"  [-] Total Spacing Violations: {len(violations)}")
    print(f"  [~] Prevailing Wind Drift Warnings: {len(wind_hazards)}\n")

    print("--- Top Critical Siting Violations Detected ---")
    for idx, v in enumerate(violations[:3], 1):
        print(f"  {idx}. {v.eq1.name} <---> {v.eq2.name}")
        print(f"     * Actual Distance: {v.actual_distance} m | Required: {v.required_distance} m (Deficit: -{v.deficit} m)")
        print(f"     * Severity: {v.severity}")
        print(f"     * Standard: {v.standard}")
        print(f"     * Rationale: {v.explanation}\n")

    # 2. Audit Compliant Plant Layout
    print("[2] Auditing Optimized & Compliant Plant Plot Plan...")
    comp_viol, comp_wind = auditor.audit_layout(COMPLIANT_PLANT_LAYOUT)
    print(f"  [+] Remaining Violations: {len(comp_viol)} (Well-segregated plot plan)")
    print(f"  [+] Wind Drift Hazards: {len(comp_wind)}\n")

    # 3. Export Sample HTML Report
    html_path = os.path.join(os.path.dirname(__file__), "sample_audit_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chemical Plant Layout Safety Audit Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #eef2f5; padding: 30px; line-height: 1.6; color: #333; }}
.container {{ max-width: 1050px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
h1 {{ color: #0d47a1; border-bottom: 3px solid #1976d2; padding-bottom: 12px; margin-top: 0; }}
.badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; color: white; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
.crit {{ background: #d32f2f; }}
.warn {{ background: #f57c00; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
th, td {{ border: 1px solid #cfd8dc; padding: 10px; text-align: left; }}
th {{ background: #1565c0; color: white; font-weight: 600; }}
tr:nth-child(even) {{ background: #f8fafc; }}
.deficit {{ color: #c62828; font-weight: bold; }}
ul {{ line-height: 1.8; }}
</style>
</head>
<body>
<div class="container">
<h1>🏭 Chemical Process Plant Layout & Safety Siting Audit Report</h1>
<p><strong>Total Equipment Units Analyzed:</strong> {len(HAZARDOUS_REFINERY_LAYOUT)}</p>
<p><strong>Prevailing Wind Direction:</strong> 45° (North-East)</p>
<p><strong>Safety Deficiencies Identified:</strong> <span class="badge crit">{len(violations)} Violations</span></p>

<h3>Separation Distance Non-Compliance Matrix (CCPS / NFPA / API):</h3>
<table>
<tr>
  <th>Unit A</th><th>Unit B</th><th>Actual Dist</th><th>Required Dist</th><th>Deficit</th><th>Severity</th><th>Standard Reference</th><th>Chemical Engineering Hazard Rationale</th>
</tr>
""")
        for v in violations:
            badge_class = "crit" if "CRITICAL" in v.severity else "warn"
            f.write(f"""<tr>
  <td><b>{v.eq1.name}</b></td>
  <td><b>{v.eq2.name}</b></td>
  <td>{v.actual_distance} m</td>
  <td>{v.required_distance} m</td>
  <td class="deficit">-{v.deficit} m</td>
  <td><span class="badge {badge_class}">{v.severity.split()[0]}</span></td>
  <td>{v.standard}</td>
  <td>{v.explanation}</td>
</tr>""")

        f.write("""</table>
<h3 style="margin-top:25px;">🌪️ Prevailing Wind Drift Impact:</h3>
<ul>""")
        for w in wind_hazards:
            f.write(f"<li><b style='color:#b71c1c;'>{w.hazard_type}:</b> {w.explanation}</li>")
        f.write("""</ul>
</div>
</body>
</html>""")

    print(f"[Report] English HTML Audit Report generated at:\n   {html_path}")
    print("=" * 75)

if __name__ == "__main__":
    run_test()
