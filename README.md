# Chemical Engineering Substitution for Plants 🏭🧪
### Industrial Facility Siting & Layout Rules Engine for Process Safety
**Automated Plot Plan Verification & Gap Analysis according to Iranian Petroleum Standards (IPS) & International Safety Guidelines**

[![Compliance](https://img.shields.io/badge/Standards-IPS--G--SF--150%20%7C%20INSO%2023591-blue.svg)](http://ips.mop.ir)
[![TotalEnergies](https://img.shields.io/badge/TotalEnergies-GS--GR--HSE--301-red.svg)]()
[![CCPS AIChE](https://img.shields.io/badge/AIChE-CCPS%20Facility%20Siting-green.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

---

## 📌 Executive Summary
**ChemSafePlot** is an engineering verification and safety audit rules engine designed for petrochemical, oil & gas refinery, and chemical processing facilities. 

It evaluates 2D/3D plant plot plans (extracted from CAD/DXF or coordinate spreadsheets) against mandatory separation distance standards, identifies non-compliance deficiencies (NCRs), and performs atmospheric dispersion & wind alignment verification for continuous ignition sources.

---

## 📚 Governing Standards & Reference Specifications

1. **IPS-G-SF-150 / INSO 23591 (2023 Edition):**
   * *General Standard for Fire Protection and Siting in Petroleum and Petrochemical Industries.*
   * Implements the official **Fire Zone Separation Matrix** across 23 distinct industrial equipment categories (`T1` to `T10`).
2. **IPS-E-PR-190 (Rev 1, 2009):**
   * *Engineering Standard for Layout and Spacing.*
   * Internal unit spacing (pumps, columns, drums, shell-and-tube exchangers, pipe rack headroom) and wind alignment constraints.
3. **TotalEnergies GS-GR-HSE-301 (2022):**
   * *Facility Siting & Physical Effect Threshold Limits:*
     * **Thermal Radiation:** $16\text{ kW/m}^2$ (Escalation zone), $5\text{ kW/m}^2$ (Restricted zone), $3\text{ kW/m}^2$ (Impacted zone).
     * **Blast Overpressure:** $200\text{ mbar}$ (Process escalation), $140\text{ mbar}$ (Restricted boundary), $50\text{ mbar}$ (Public threshold).
     * **Flare Ground Radiation:** $\le 4.73\text{ kW/m}^2$.
4. **CCPS (Center for Chemical Process Safety - AIChE):**
   * *Guidelines for Facility Siting and Layout.*

---

## ⚙️ Core Architecture & Features

* **3D/2D Euclidean Distance Physics:** Calculates true edge-to-edge separation distances:
  $$D_{\text{edge}} = \max\left(0, \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2 + (z_1 - z_2)^2} - (r_1 + r_2)\right)$$
* **Automated CSV/CAD Data Pipeline:** Directly imports coordinates extracted from AutoCAD, PDMS, or SmartPlant.
* **Atmospheric Wind Drift Vector:** Detects if prevailing wind carries volatile fuel/LPG leaks toward continuous burner flames (`T4_FIRED_HEATER` or `T9_FLARE`).
* **Interactive Web GUI (HTML5 Canvas):** Zero-install, browser-based visualizer with drag-and-drop units, CAD blueprint background overlay, and real-time gap analysis.
* **Non-Compliance Reporting (NCR):** Categorizes severity (`CRITICAL`, `HIGH`, `WARNING`) with deficit metrics and standard clause citations.

---

## 🗂️ Equipment Categorization (IPS-G-SF-150)

| Category Code | Description | Hazard Classification |
| :--- | :--- | :--- |
| `T1_ERUPTIVE` | Eruptive Oil & Gas Wellheads | High Pressure / Flammable Release |
| `T1_NON_ERUPTIVE` | Non-Eruptive Wells | Fuel Source |
| `T2_HIGH_P` | Unfired Process ($P > 70\text{ barg}$) | High-Pressure Containment |
| `T2_LOW_P` | Unfired Process ($P \le 70\text{ barg}$) | Process Hydrocarbon |
| `T2_LPG` | LPG Fractionation Units | Highly Volatile Gas Release |
| `T3_LPG_ABOVE` | Aboveground LPG Spheres | BLEVE Potential |
| `T3_CRUDE_L` | Crude Oil Storage (Dike $3000\text{--}7000\text{ m}^2$) | Pool Fire / Boilover |
| `T4_FIRED_HEATER` | Fired Heaters, Reformers & Boilers | Permanent Ignition Source |
| `T5_POWER_GEN` | Turbines & Gas Compressor Stations | Mechanical & Seal Leak Hazard |
| `T6_CONTROL_ROOM` | Central Control Building (CCR) | Occupied Structure Protection |
| `T7_FIRE_WATER` | Fire Water Pump Station | Critical Emergency Survival Asset |
| `T9_FLARE` | Elevated Flare Stack | Thermal Radiation Footprint |
| `T10_LOADING_RACK`| Road Tanker Gantry | Heavy Logistics & Transfer |

---

## 🚀 Quick Start Guide

### 1. Web Visualizer (Zero Installation)
Open `index.html` (or `chemsafe_web.html`) directly in any modern browser, or launch:
```bash
python -m http.server 8000
# Open: http://localhost:8000
```

### 2. Python Programmatic Usage
```python
from safety_standards import AntiGravityLayoutVerifier

# Initialize verifier with 45° prevailing wind
verifier = AntiGravityLayoutVerifier(prevailing_wind_deg=45.0)

# Import plant coordinates from CSV
verifier.import_from_csv("sample_plot_plan_coordinates.csv")

# Run Fire Zone Separation Audit (IPS-G-SF-150 / INSO 23591)
violations = verifier.verify_fire_zones()
for v in violations:
    print(f"[{v.severity}] {v.node1.tag} <-> {v.node2.tag}: Actual={v.actual_distance}m, Required={v.required_distance}m")

# Run Prevailing Wind Dispersion Check (IPS-E-PR-190)
wind_hazards = verifier.verify_wind_orientation()
for w in wind_hazards:
    print(f"[Wind Hazard] {w.explanation}")
```

### 3. Run Automated System Test Suite
```bash
python verify_all.py
```

---

## 📄 Non-Compliance Report Sample Output

```text
[CRITICAL] TK-101 (T3_LPG_ABOVE) <-> WH-01 (T1_ERUPTIVE)
  • Actual Separation: 33.5m | IPS-G-SF-150 Mandatory: 100.0m
  • Deficit: -66.5m
  • Standard: IPS-G-SF-150 / INSO 23591

[CRITICAL] R-301 (T2_HIGH_P) <-> FL-501 (T9_FLARE)
  • Actual Separation: 128.8m | IPS-G-SF-150 Mandatory: 150.0m
  • Deficit: -21.2m
  • Standard: IPS-G-SF-150 / INSO 23591
```

---

## 👤 Author & Contribution
Developed for advanced Chemical Process Safety, Industrial Plot Plan Auditing, and Plant Siting Automation.  
Licensed under the **MIT License**.
