"""
Sample Chemical Plant Layouts for Spacing & Siting Compliance Testing
"""

from safety_standards import Equipment

# Layout 1: High-Hazard Refinery Plot Plan with Severe Siting Deficiencies
HAZARDOUS_REFINERY_LAYOUT = [
    Equipment(id="FH-101", name="Cracking Furnace (Fired Heater)", eq_type="FIRED_HEATER", x=60.0, y=70.0, radius=7.0),
    Equipment(id="TK-201", name="LPG Bullet Storage Tank", eq_type="FLAMMABLE_STORAGE", x=80.0, y=75.0, radius=10.0),  # Violates NFPA 30
    Equipment(id="R-301", name="Hydrotreating Reactor", eq_type="REACTOR", x=40.0, y=110.0, radius=6.0),
    Equipment(id="CR-01", name="Central Control Building", eq_type="CONTROL_ROOM", x=50.0, y=125.0, radius=8.0),       # Violates API 752
    Equipment(id="FL-501", name="Emergency Flare Stack", eq_type="FLARE_STACK", x=90.0, y=140.0, radius=5.0),           # Severe radiation footprint
    Equipment(id="FW-901", name="Fire Water Pump House", eq_type="FIRE_WATER_PUMP", x=65.0, y=85.0, radius=6.0),        # Trapped in blast zone
    Equipment(id="CP-401", name="Hydrogen Compressor House", eq_type="COMPRESSOR_HOUSE", x=50.0, y=80.0, radius=7.0),   # Directly adjacent to furnace
    Equipment(id="LR-601", name="Fuel Truck Loading Gantry", eq_type="LOADING_RACK", x=120.0, y=60.0, radius=8.0),
]

# Layout 2: Optimized & Fully Compliant Petrochemical Facility Plot Plan (CCPS / NFPA / API)
COMPLIANT_PLANT_LAYOUT = [
    Equipment(id="FH-101", name="Cracking Furnace", eq_type="FIRED_HEATER", x=40.0, y=50.0, radius=7.0),
    Equipment(id="TK-201", name="Hydrocarbon Tank Farm", eq_type="FLAMMABLE_STORAGE", x=150.0, y=50.0, radius=12.0),
    Equipment(id="R-301", name="Chemical Reaction Unit", eq_type="REACTOR", x=50.0, y=110.0, radius=6.0),
    Equipment(id="CP-401", name="Gas Compressor Station", eq_type="COMPRESSOR_HOUSE", x=90.0, y=105.0, radius=7.0),
    Equipment(id="CR-01", name="Control Room (Upwind Zone)", eq_type="CONTROL_ROOM", x=30.0, y=170.0, radius=9.0),
    Equipment(id="FL-501", name="Elevated Flare (Downwind)", eq_type="FLARE_STACK", x=180.0, y=180.0, radius=5.0),
    Equipment(id="FW-901", name="Fire Water Station (Isolated)", eq_type="FIRE_WATER_PUMP", x=20.0, y=20.0, radius=6.0),
    Equipment(id="LR-601", name="Road Tanker Gantry", eq_type="LOADING_RACK", x=160.0, y=110.0, radius=8.0),
]
