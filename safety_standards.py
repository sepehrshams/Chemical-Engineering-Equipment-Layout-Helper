"""
Facility Siting & Layout Rules Engine for Process Safety
Compiled based on:
- IPS-G-SF-150 / INSO 23591 (2023) - Iranian Petroleum Standard: Fire Protection & Siting
- IPS-E-PR-190 (Rev 1, 2009) - Engineering Standard for Layout and Spacing
- TotalEnergies GS-GR-HSE-301 (2022) - Consequence Threshold Limits & Siting
- CCPS Guidelines for Facility Siting and Layout (AIChE)
- NFPA 30 & API 521 / API RP 752
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List, Any
from enum import Enum
import math
import csv
import json

class UnitCategory(Enum):
    # IPS-G-SF-150 & TotalEnergies Categories
    WELLHEAD_ERUPTIVE = "T1_ERUPTIVE"             # چاههای نفت و گاز فورانی
    WELLHEAD_NON_ERUPTIVE = "T1_NON_ERUPTIVE"     # چاههای غیرفورانی
    WATER_INJECTION = "T1_WATER_INJ"              # چاههای تزریق آب
    UNFIRED_PROCESS_HIGH_P = "T2_HIGH_P"          # فرآیند بدون شعله (P > 70 barg)
    UNFIRED_PROCESS_LOW_P = "T2_LOW_P"            # فرآیند بدون شعله (P <= 70 barg)
    LPG_PROCESS = "T2_LPG"                        # واحدهای فرایند گاز مایع
    OIL_TREATMENT = "T2_OIL"                      # تفکیک و تثبیت نفت و میعانات
    SLUG_CATCHER = "T2_SLUG_CATCHER"              # لختهگیر با حجم بالا
    STORAGE_LPG_MOUNDED = "T3_LPG_MOUNDED"        # مخازن مدفون LPG
    STORAGE_LPG_ABOVE = "T3_LPG_ABOVE"            # مخازن روباز LPG
    STORAGE_ATM_CRUDE_SMALL = "T3_CRUDE_S"        # مخزن نفت خام (باندوال < 1000 متر مربع)
    STORAGE_ATM_CRUDE_MED = "T3_CRUDE_M"          # مخزن نفت خام (باندوال 1000 تا 3000 متر مربع)
    STORAGE_ATM_CRUDE_LARGE = "T3_CRUDE_L"        # مخزن نفت خام (باندوال 3000 تا 7000 متر مربع)
    FIRED_HEATERS = "T4_FIRED_HEATER"             # کورهها و گرمکنهای مشعلدار
    MACHINERY_POWER = "T5_POWER_GEN"              # ژنراتورها، توربینها، کمپرسورهای برق
    BUILDINGS_ADMIN = "T6_ADMIN_SERVICE"          # دفاتر، اقامتگاه، رستوران
    CONTROL_ROOM = "T6_CONTROL_ROOM"              # اتاق کنترل مرکزی
    SUBSTATION = "T6_SUBSTATION"                  # پستهای برق
    FIRE_WATER_STATION = "T7_FIRE_WATER"          # ایستگاه پمپهای آب آتشنشانی
    COLD_VENT = "T8_COLD_VENT"                    # ونت سرد
    FLARE_STACK = "T9_FLARE"                      # مشعل و فلر مرتفع
    LOADING_RACK = "T10_LOADING_RACK"             # سکوهای بارگیری و تخلیه
    FENCE = "PROPERTY_FENCE"                      # فنس محیطی سایت

# Standard Commercial Sizes available in market according to API / ASME / IPS-E-PR-190
COMMERCIAL_CATALOG: Dict[UnitCategory, List[Dict[str, Any]]] = {
    UnitCategory.STORAGE_ATM_CRUDE_LARGE: [
        {"name": "API 650 - 150,000 bbl (Ø 48m, H 16m)", "radius": 24.0, "diameter": 48.0},
        {"name": "API 650 - 250,000 bbl (Ø 62m, H 18m)", "radius": 31.0, "diameter": 62.0},
        {"name": "API 650 - 500,000 bbl (Ø 85m, H 22m)", "radius": 42.5, "diameter": 85.0},
    ],
    UnitCategory.STORAGE_ATM_CRUDE_MED: [
        {"name": "API 650 - 50,000 bbl (Ø 28m, H 14m)", "radius": 14.0, "diameter": 28.0},
        {"name": "API 650 - 80,000 bbl (Ø 35m, H 14m)", "radius": 17.5, "diameter": 35.0},
        {"name": "API 650 - 100,000 bbl (Ø 40m, H 14m)", "radius": 20.0, "diameter": 40.0},
    ],
    UnitCategory.STORAGE_ATM_CRUDE_SMALL: [
        {"name": "API 650 - 5,000 bbl (Ø 9m, H 12m)", "radius": 4.5, "diameter": 9.0},
        {"name": "API 650 - 10,000 bbl (Ø 13m, H 12m)", "radius": 6.5, "diameter": 13.0},
        {"name": "API 650 - 20,000 bbl (Ø 18m, H 12m)", "radius": 9.0, "diameter": 18.0},
    ],
    UnitCategory.STORAGE_LPG_ABOVE: [
        {"name": "ASME VIII - 1,000 m³ Sphere (Ø 12.4m)", "radius": 6.2, "diameter": 12.4},
        {"name": "ASME VIII - 2,500 m³ Sphere (Ø 16.8m)", "radius": 8.4, "diameter": 16.8},
        {"name": "ASME VIII - 5,000 m³ Sphere (Ø 21.2m)", "radius": 10.6, "diameter": 21.2},
        {"name": "ASME VIII - 8,000 m³ Sphere (Ø 24.8m)", "radius": 12.4, "diameter": 24.8},
    ],
    UnitCategory.STORAGE_LPG_MOUNDED: [
        {"name": "3 Bullets Bank (Ø 4m x L 30m, 1,000 m³)", "radius": 9.0, "diameter": 18.0},
        {"name": "4 Bullets Bank (Ø 5m x L 45m, 3,200 m³)", "radius": 13.0, "diameter": 26.0},
        {"name": "6 Bullets Bank (Ø 6m x L 60m, 8,000 m³)", "radius": 18.0, "diameter": 36.0},
    ],
    UnitCategory.FIRED_HEATERS: [
        {"name": "Cylindrical Vertical Heater (15 MW)", "radius": 5.0, "diameter": 10.0},
        {"name": "Single-Cell Box Cabin Heater (40 MW)", "radius": 8.0, "diameter": 16.0},
        {"name": "Double-Cell Cracking Furnace (90 MW)", "radius": 12.0, "diameter": 24.0},
        {"name": "Multi-Cell Steam Methane Reformer (180 MW)", "radius": 16.0, "diameter": 32.0},
    ],
    UnitCategory.FLARE_STACK: [
        {"name": "12\" Tip - Low Relief (30 MW, Rad Base 75m)", "radius": 4.0, "flare_rating": 30.0},
        {"name": "24\" Tip - Standard Relief (90 MW, Rad Base 110m)", "radius": 6.0, "flare_rating": 90.0},
        {"name": "36\" Tip - High Pressure (250 MW, Rad Base 150m)", "radius": 8.0, "flare_rating": 250.0},
        {"name": "48\" Tip - Full Emergency Blowdown (600 MW, Rad Base 190m)", "radius": 11.0, "flare_rating": 600.0},
    ],
    UnitCategory.UNFIRED_PROCESS_HIGH_P: [
        {"name": "Medium Fixed Bed Reactor (Ø 3.2m x H 14m)", "radius": 5.0, "diameter": 3.2},
        {"name": "Heavy Wall Hydrocracker (Ø 4.8m x H 25m)", "radius": 8.0, "diameter": 4.8},
        {"name": "CCR Platforming Regeneration Train", "radius": 11.0, "diameter": 8.0},
        {"name": "Fluid Catalytic Cracking (FCC) Reactor/Regen", "radius": 15.0, "diameter": 12.0},
    ],
    UnitCategory.UNFIRED_PROCESS_LOW_P: [
        {"name": "Distillation Column Train (Ø 2.5m)", "radius": 4.0, "diameter": 2.5},
        {"name": "Gas Sweetening & Amine Absorption Train", "radius": 7.0, "diameter": 4.5},
        {"name": "Heavy Aromatics Fractionation Train", "radius": 10.0, "diameter": 7.0},
    ],
    UnitCategory.MACHINERY_POWER: [
        {"name": "2-Stage Reciprocating Compressor Skid (1.5 MW)", "radius": 5.0, "diameter": 10.0},
        {"name": "Centrifugal Gas Turbine Train (12 MW)", "radius": 8.0, "diameter": 16.0},
        {"name": "Gas Reinjection Compressor Hall (35 MW)", "radius": 12.0, "diameter": 24.0},
    ],
    UnitCategory.CONTROL_ROOM: [
        {"name": "Local Field Auxiliary Room (FAR - 10m x 15m)", "radius": 6.0, "diameter": 15.0},
        {"name": "Blast-Resistant CCR - Single Story (20m x 30m)", "radius": 9.0, "diameter": 25.0},
        {"name": "Integrated Control & Emergency Command Hub (35m x 50m)", "radius": 14.0, "diameter": 40.0},
    ],
    UnitCategory.FIRE_WATER_STATION: [
        {"name": "Standard 2-Pump Skids (2x 2,500 gpm)", "radius": 6.0, "diameter": 12.0},
        {"name": "Major Terminal Fire Pump Station (4x 4,000 gpm)", "radius": 10.0, "diameter": 20.0},
    ],
    UnitCategory.LOADING_RACK: [
        {"name": "2-Bay Road Tanker Gantry", "radius": 6.0, "diameter": 12.0},
        {"name": "4-Bay Heavy Fuel Loading Island", "radius": 9.0, "diameter": 18.0},
        {"name": "8-Bay Multi-Product Rail & Truck Gantry", "radius": 14.0, "diameter": 28.0},
    ],
    UnitCategory.WELLHEAD_ERUPTIVE: [
        {"name": "Single High-Pressure Wellhead (10,000 psi)", "radius": 6.0, "diameter": 12.0},
        {"name": "Cluster Multi-Well Pad (4 Wells)", "radius": 10.0, "diameter": 20.0},
    ],
}

# Category Metadata for Display, Visualization and Physics
CATEGORY_META: Dict[UnitCategory, Dict[str, Any]] = {
    UnitCategory.WELLHEAD_ERUPTIVE: {"name_en": "Eruptive Wellhead", "name_fa": "چاه فورانی نفت/گاز", "color": "#dc2626", "radius": 8.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.WELLHEAD_NON_ERUPTIVE: {"name_en": "Non-Eruptive Wellhead", "name_fa": "چاه غیرفورانی", "color": "#ea580c", "radius": 6.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.WATER_INJECTION: {"name_en": "Water Injection Well", "name_fa": "چاه تزریق آب", "color": "#0284c7", "radius": 5.0, "is_fuel": False, "is_ignition": False},
    UnitCategory.UNFIRED_PROCESS_HIGH_P: {"name_en": "High-Pressure Process (>70 barg)", "name_fa": "واحد فرآیند فشار قوی (>70 barg)", "color": "#f97316", "radius": 7.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.UNFIRED_PROCESS_LOW_P: {"name_en": "Low-Pressure Process (<=70 barg)", "name_fa": "واحد فرآیند کم‌فشار", "color": "#fb923c", "radius": 6.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.LPG_PROCESS: {"name_en": "LPG Fractionation Unit", "name_fa": "واحد فرآیند گاز مایع (LPG)", "color": "#c026d3", "radius": 8.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.OIL_TREATMENT: {"name_en": "Oil Separation & Stabilization", "name_fa": "تفکیک و تثبیت نفت و میعانات", "color": "#b45309", "radius": 7.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.SLUG_CATCHER: {"name_en": "High-Volume Slug Catcher", "name_fa": "لخته‌گیر با حجم بالا", "color": "#d97706", "radius": 8.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.STORAGE_LPG_MOUNDED: {"name_en": "Mounded LPG Bullets", "name_fa": "مخازن مدفون LPG (موندد)", "color": "#9333ea", "radius": 9.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.STORAGE_LPG_ABOVE: {"name_en": "Aboveground LPG Spheres", "name_fa": "مخازن روباز LPG (کروی)", "color": "#7e22ce", "radius": 12.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.STORAGE_ATM_CRUDE_SMALL: {"name_en": "Crude Tank (<1000 m² Dike)", "name_fa": "مخزن نفت خام (باندوال کوچک)", "color": "#6b21a8", "radius": 8.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.STORAGE_ATM_CRUDE_MED: {"name_en": "Crude Tank (1000-3000 m² Dike)", "name_fa": "مخزن نفت خام (باندوال متوسط)", "color": "#581c87", "radius": 11.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.STORAGE_ATM_CRUDE_LARGE: {"name_en": "Crude Tank (3000-7000 m² Dike)", "name_fa": "مخزن نفت خام (باندوال بزرگ)", "color": "#3b0764", "radius": 14.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.FIRED_HEATERS: {"name_en": "Fired Heaters & Boilers", "name_fa": "کوره‌ها و گرمکن‌های مشعل‌دار", "color": "#ef4444", "radius": 7.0, "is_fuel": True, "is_ignition": True},
    UnitCategory.MACHINERY_POWER: {"name_en": "Turbines / Power Compressors", "name_fa": "توربین‌ها، ژنراتورها و کمپرسورخانه", "color": "#e11d48", "radius": 7.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.BUILDINGS_ADMIN: {"name_en": "Admin, Camp & Services", "name_fa": "ساختمان اداری، اقامتگاه و خدمات", "color": "#2563eb", "radius": 9.0, "is_fuel": False, "is_ignition": False},
    UnitCategory.CONTROL_ROOM: {"name_en": "Central Control Room", "name_fa": "اتاق کنترل مرکزی (CCR)", "color": "#1d4ed8", "radius": 8.0, "is_fuel": False, "is_ignition": False},
    UnitCategory.SUBSTATION: {"name_en": "Electrical Substation", "name_fa": "پست برق اصلی", "color": "#1e40af", "radius": 6.0, "is_fuel": False, "is_ignition": False},
    UnitCategory.FIRE_WATER_STATION: {"name_en": "Fire Water Pump Station", "name_fa": "ایستگاه پمپاژ آب آتش‌نشانی", "color": "#16a34a", "radius": 7.0, "is_fuel": False, "is_ignition": False},
    UnitCategory.COLD_VENT: {"name_en": "Cold Vent Stack", "name_fa": "ونت سرد هیدروکربنی", "color": "#db2777", "radius": 5.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.FLARE_STACK: {"name_en": "Elevated Flare Stack", "name_fa": "مشعل و فلر مرتفع", "color": "#e11d48", "radius": 6.0, "is_fuel": True, "is_ignition": True},
    UnitCategory.LOADING_RACK: {"name_en": "Tanker Loading/Unloading Gantry", "name_fa": "سکوهای بارگیری و تخلیه تانکر", "color": "#0d9488", "radius": 8.0, "is_fuel": True, "is_ignition": False},
    UnitCategory.FENCE: {"name_en": "Site Boundary Fence", "name_fa": "فنس محیطی سایت", "color": "#64748b", "radius": 4.0, "is_fuel": False, "is_ignition": False},
}

# ماتریس فواصل پایه بین نواحی حریق (Base Separation Matrix - IPS-G-SF-150 / INSO 23591)
FIRE_ZONE_SEPARATION_IPS_G_SF_150: Dict[Tuple[UnitCategory, UnitCategory], float] = {
    # چاه فورانی با سایر تجهیزات
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.BUILDINGS_ADMIN): 200.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.CONTROL_ROOM): 150.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.STORAGE_ATM_CRUDE_SMALL): 45.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.STORAGE_LPG_ABOVE): 100.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.FLARE_STACK): 150.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.FIRED_HEATERS): 100.0,
    (UnitCategory.WELLHEAD_ERUPTIVE, UnitCategory.FENCE): 200.0,
    
    # فرآیند فشار قوی (P > 70 barg)
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.FIRED_HEATERS): 60.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.CONTROL_ROOM): 30.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.BUILDINGS_ADMIN): 100.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.STORAGE_LPG_ABOVE): 60.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.STORAGE_ATM_CRUDE_LARGE): 60.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.FLARE_STACK): 150.0,
    (UnitCategory.UNFIRED_PROCESS_HIGH_P, UnitCategory.FENCE): 250.0,

    # فرآیند کم‌فشار
    (UnitCategory.UNFIRED_PROCESS_LOW_P, UnitCategory.FIRED_HEATERS): 30.0,
    (UnitCategory.UNFIRED_PROCESS_LOW_P, UnitCategory.CONTROL_ROOM): 30.0,
    (UnitCategory.UNFIRED_PROCESS_LOW_P, UnitCategory.BUILDINGS_ADMIN): 60.0,
    (UnitCategory.UNFIRED_PROCESS_LOW_P, UnitCategory.FLARE_STACK): 100.0,

    # واحدهای LPG و تفکیک نفت
    (UnitCategory.LPG_PROCESS, UnitCategory.FIRED_HEATERS): 50.0,
    (UnitCategory.LPG_PROCESS, UnitCategory.CONTROL_ROOM): 45.0,
    (UnitCategory.LPG_PROCESS, UnitCategory.STORAGE_LPG_ABOVE): 60.0,
    (UnitCategory.OIL_TREATMENT, UnitCategory.FIRED_HEATERS): 30.0,
    (UnitCategory.SLUG_CATCHER, UnitCategory.FIRED_HEATERS): 60.0,
    (UnitCategory.SLUG_CATCHER, UnitCategory.CONTROL_ROOM): 60.0,

    # کوره‌ها و تجهیزات دارای شعله
    (UnitCategory.FIRED_HEATERS, UnitCategory.CONTROL_ROOM): 30.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.BUILDINGS_ADMIN): 60.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.MACHINERY_POWER): 30.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.STORAGE_LPG_ABOVE): 60.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.STORAGE_ATM_CRUDE_LARGE): 60.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.STORAGE_ATM_CRUDE_SMALL): 30.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.LOADING_RACK): 45.0,
    (UnitCategory.FIRED_HEATERS, UnitCategory.FENCE): 75.0,

    # مخازن ذخیره هیدروکربن
    (UnitCategory.STORAGE_ATM_CRUDE_LARGE, UnitCategory.CONTROL_ROOM): 90.0,
    (UnitCategory.STORAGE_ATM_CRUDE_LARGE, UnitCategory.BUILDINGS_ADMIN): 90.0,
    (UnitCategory.STORAGE_ATM_CRUDE_LARGE, UnitCategory.LOADING_RACK): 45.0,
    (UnitCategory.STORAGE_ATM_CRUDE_LARGE, UnitCategory.FENCE): 130.0,
    (UnitCategory.STORAGE_ATM_CRUDE_LARGE, UnitCategory.FLARE_STACK): 100.0,

    (UnitCategory.STORAGE_ATM_CRUDE_MED, UnitCategory.CONTROL_ROOM): 60.0,
    (UnitCategory.STORAGE_ATM_CRUDE_MED, UnitCategory.BUILDINGS_ADMIN): 75.0,
    (UnitCategory.STORAGE_ATM_CRUDE_MED, UnitCategory.FENCE): 90.0,

    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.CONTROL_ROOM): 60.0,
    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.BUILDINGS_ADMIN): 100.0,
    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.MACHINERY_POWER): 60.0,
    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.LOADING_RACK): 45.0,
    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.FLARE_STACK): 120.0,
    (UnitCategory.STORAGE_LPG_ABOVE, UnitCategory.FENCE): 300.0,

    (UnitCategory.STORAGE_LPG_MOUNDED, UnitCategory.CONTROL_ROOM): 30.0,
    (UnitCategory.STORAGE_LPG_MOUNDED, UnitCategory.BUILDINGS_ADMIN): 60.0,
    (UnitCategory.STORAGE_LPG_MOUNDED, UnitCategory.FENCE): 75.0,

    # فلر و ونت
    (UnitCategory.FLARE_STACK, UnitCategory.CONTROL_ROOM): 120.0,
    (UnitCategory.FLARE_STACK, UnitCategory.BUILDINGS_ADMIN): 150.0,
    (UnitCategory.FLARE_STACK, UnitCategory.FENCE): 100.0,

    # ایستگاه آب آتش‌نشانی
    (UnitCategory.FIRE_WATER_STATION, UnitCategory.UNFIRED_PROCESS_HIGH_P): 40.0,
    (UnitCategory.FIRE_WATER_STATION, UnitCategory.STORAGE_LPG_ABOVE): 60.0,
    (UnitCategory.FIRE_WATER_STATION, UnitCategory.STORAGE_ATM_CRUDE_LARGE): 60.0,
    (UnitCategory.FIRE_WATER_STATION, UnitCategory.FIRED_HEATERS): 30.0,
}

# حداقل فواصل تجهیزات درون‌واحدی (IPS-E-PR-190 & CCPS Appendix A)
INTERNAL_EQUIPMENT_SPACING_METERS = {
    "PUMP_TO_PUMP_SMALL": 1.0,           # تلمبههای کوچک تا 22.5 کیلووات
    "PUMP_TO_PUMP_LARGE": 1.5,           # تلمبههای بزرگ بالای 22.5 کیلووات
    "COLUMN_TO_COLUMN": 3.0,             # برج به برج
    "DRUM_TO_DRUM": 2.0,                 # ظرف به ظرف
    "SHELL_EXCHANGER_TO_SHELL": 1.0,     # مبدل پوسته-لوله به مبدل
    "PROCESS_TO_FIRED_HEATER_MIN": 15.0, # حداقل فاصله تجهیزات فرایندی با کوره مشعلدار
    "AIR_COOLER_TO_HYDROCARBON_PUMP": 7.5,# فاصله افقی کولر هوایی با پمپ هیدروکربنی
    "PIPERACK_HEADROOM_MAIN_ROAD": 5.0,  # ارتفاع آزاد پایپرک روی جاده اصلی
    "PIPERACK_HEADROOM_RAILROAD": 6.8,   # ارتفاع آزاد پایپرک روی خط راهآهن
}

# آستانه‌های شدت پیامد برای تعیین حریم (Threshold Limits - TotalEnergies GS-GR-HSE-301)
SAFETY_THRESHOLDS = {
    "RADIATION_ESCALATION_KW_M2": 16.0,   # مرز ناحیه تشدید حریق
    "RADIATION_RESTRICTED_KW_M2": 5.0,    # مرز منطقه محصور داخل فنس
    "RADIATION_IMPACTED_KW_M2": 3.0,      # مرز منطقه تحت تاثیر عمومی
    "OVERPRESSURE_ESCALATION_MBAR": 200,  # موج انفجار برای زون فرآیند
    "OVERPRESSURE_RESTRICTED_MBAR": 140,  # موج انفجار برای مرز محصور
    "OVERPRESSURE_IMPACTED_MBAR": 50,     # موج انفجار حد آستانه شکست شیشه/عمومی
    "FLARE_RADIATION_GROUND_KW_M2": 4.7,  # حداکثر تششع حرارتی فلر در سطح زمین (API 521 / TotalEnergies)
}

@dataclass
class EquipmentNode:
    tag: str
    category: UnitCategory
    coord_x: float
    coord_y: float
    elevation_z: float = 0.0
    is_ignition_source: bool = False
    is_fuel_source: bool = False
    flash_point: Optional[float] = None # بر حسب درجه سانتیگراد
    radius: float = 6.0
    commercial_size_label: str = ""
    notes: str = ""

    def __post_init__(self):
        meta = CATEGORY_META.get(self.category, {})
        if not self.is_ignition_source:
            self.is_ignition_source = meta.get("is_ignition", False)
        if not self.is_fuel_source:
            self.is_fuel_source = meta.get("is_fuel", False)
        if self.radius == 6.0 and "radius" in meta:
            self.radius = meta["radius"]

    @property
    def diameter(self) -> float:
        return self.radius * 2.0

@dataclass
class NonComplianceRecord:
    node1: EquipmentNode
    node2: EquipmentNode
    actual_distance: float
    required_distance: float
    deficit: float
    severity: str  # 'CRITICAL', 'HIGH', 'WARNING'
    standard: str
    technical_rationale: str

@dataclass
class WindIgnitionHazard:
    heater_node: EquipmentNode
    fuel_node: EquipmentNode
    distance: float
    hazard_type: str
    explanation: str

class AntiGravityLayoutVerifier:
    """
    Industrial Plot Plan & Facility Siting Rules Engine
    Calculates dynamic separation distances based on Equipment Dimensions (Diameter & Rating)
    Fully compliant with IPS-G-SF-150 / INSO 23591 (2023), IPS-E-PR-190, TotalEnergies GS-GR-HSE-301
    """
    def __init__(self, prevailing_wind_deg: float = 45.0):
        self.wind_dir = prevailing_wind_deg # جهت وزش باد غالب (درجه)
        self.nodes: List[EquipmentNode] = []

    def add_node(self, node: EquipmentNode):
        self.nodes.append(node)

    def clear(self):
        self.nodes.clear()

    def calculate_distance(self, n1: EquipmentNode, n2: EquipmentNode) -> float:
        return math.sqrt((n1.coord_x - n2.coord_x)**2 + (n1.coord_y - n2.coord_y)**2 + (n1.elevation_z - n2.elevation_z)**2)

    def calculate_edge_distance(self, n1: EquipmentNode, n2: EquipmentNode) -> float:
        center_dist = self.calculate_distance(n1, n2)
        return max(0.0, center_dist - (n1.radius + n2.radius))

    def calculate_required_separation(self, n1: EquipmentNode, n2: EquipmentNode) -> Optional[Tuple[float, str]]:
        """
        Calculates dynamic separation distance based on IPS-E-PR-190 & IPS-G-SF-150 formulas:
        Takes into account equipment diameter D, tank capacity, and flare exclusion footprint.
        """
        c1, c2 = n1.category, n2.category
        base_rule = FIRE_ZONE_SEPARATION_IPS_G_SF_150.get((c1, c2)) or \
                    FIRE_ZONE_SEPARATION_IPS_G_SF_150.get((c2, c1))

        # Check for Tank-to-Tank spacing (IPS-E-PR-190 Section 5 & NFPA 30)
        tank_cats = [UnitCategory.STORAGE_ATM_CRUDE_SMALL, UnitCategory.STORAGE_ATM_CRUDE_MED, UnitCategory.STORAGE_ATM_CRUDE_LARGE]
        if c1 in tank_cats and c2 in tank_cats:
            # Distance between floating/cone roof tanks is a function of (D1 + D2)
            d1, d2 = n1.diameter, n2.diameter
            calc_dist = max(15.0, (d1 + d2) / 3.0)
            return round(calc_dist, 1), f"IPS-E-PR-190 Table 2 & NFPA 30: Separation between adjacent crude tanks = (D1+D2)/3 = ({d1}m+{d2}m)/3."

        # Spacing between LPG Spheres (IPS-E-PR-190 Section 5.3)
        if c1 == UnitCategory.STORAGE_LPG_ABOVE and c2 == UnitCategory.STORAGE_LPG_ABOVE:
            d_larger = max(n1.diameter, n2.diameter)
            calc_dist = max(15.0, 0.75 * d_larger)
            return round(calc_dist, 1), f"IPS-E-PR-190 Sec 5.3: Spacing between pressurized LPG spheres = 0.75 x D_larger ({d_larger}m)."

        # Storage Tank to Fired Heater (Scale with Tank Diameter per IPS-E-PR-190)
        if (c1 in tank_cats or c1 == UnitCategory.STORAGE_LPG_ABOVE) and c2 == UnitCategory.FIRED_HEATERS:
            tank_d = n1.diameter
            calc_dist = max(base_rule or 60.0, 1.2 * tank_d)
            return round(calc_dist, 1), f"IPS-E-PR-190 & IPS-G-SF-150: Tank to Fired Heater separation scales with diameter = max(60m, 1.2*D_tank)."
        if (c2 in tank_cats or c2 == UnitCategory.STORAGE_LPG_ABOVE) and c1 == UnitCategory.FIRED_HEATERS:
            tank_d = n2.diameter
            calc_dist = max(base_rule or 60.0, 1.2 * tank_d)
            return round(calc_dist, 1), f"IPS-E-PR-190 & IPS-G-SF-150: Tank to Fired Heater separation scales with diameter = max(60m, 1.2*D_tank)."

        # Storage Tank to Property Fence (1.5 x D per IPS-E-PR-190 & NFPA 30)
        if c1 in tank_cats and c2 == UnitCategory.FENCE:
            calc_dist = max(base_rule or 90.0, 1.5 * n1.diameter)
            return round(calc_dist, 1), f"IPS-E-PR-190: Tank to site fence = max(base, 1.5*D) = {calc_dist}m."
        if c2 in tank_cats and c1 == UnitCategory.FENCE:
            calc_dist = max(base_rule or 90.0, 1.5 * n2.diameter)
            return round(calc_dist, 1), f"IPS-E-PR-190: Tank to site fence = max(base, 1.5*D) = {calc_dist}m."

        # Flare Exclusion Zone scaling with Flare tip rating / radius (API 521 / TotalEnergies / IPS-E-PR-190)
        if c1 == UnitCategory.FLARE_STACK or c2 == UnitCategory.FLARE_STACK:
            flare_node = n1 if c1 == UnitCategory.FLARE_STACK else n2
            scale_factor = flare_node.radius / 6.0 # 6m is reference standard 90MW tip
            flare_dist = max(base_rule or 100.0, (base_rule or 100.0) * scale_factor)
            return round(flare_dist, 1), f"API 521 & TotalEnergies GS-GR-HSE-301: Ground radiation exclusion zone scaled to flare duty/radius ({flare_node.radius}m)."

        if base_rule:
            return base_rule, "IPS-G-SF-150 / INSO 23591 Fire Zone Separation Matrix."

        return None

    def verify_fire_zones(self) -> List[NonComplianceRecord]:
        violations: List[NonComplianceRecord] = []
        n = len(self.nodes)
        for i in range(n):
            for j in range(i + 1, n):
                n1, n2 = self.nodes[i], self.nodes[j]
                rule_res = self.calculate_required_separation(n1, n2)
                
                if rule_res:
                    req_dist, rationale_rule = rule_res
                    edge_dist = self.calculate_edge_distance(n1, n2)
                    if edge_dist < req_dist:
                        deficit = req_dist - edge_dist
                        ratio = edge_dist / req_dist if req_dist > 0 else 0
                        severity = "CRITICAL" if ratio < 0.5 else ("HIGH" if ratio < 0.8 else "WARNING")
                        
                        meta1 = CATEGORY_META.get(n1.category, {})
                        meta2 = CATEGORY_META.get(n2.category, {})
                        rationale = f"{rationale_rule} Actual edge-to-edge separation: {edge_dist:.1f}m."
                        
                        violations.append(NonComplianceRecord(
                            node1=n1,
                            node2=n2,
                            actual_distance=round(edge_dist, 1),
                            required_distance=req_dist,
                            deficit=round(deficit, 1),
                            severity=severity,
                            standard="IPS-E-PR-190 / IPS-G-SF-150",
                            technical_rationale=rationale
                        ))
        return violations

    def verify_wind_orientation(self) -> List[WindIgnitionHazard]:
        hazards = []
        wind_rad = math.radians(self.wind_dir)
        wdx = math.cos(wind_rad)
        wdy = math.sin(wind_rad)

        for n1 in self.nodes:
            if n1.is_ignition_source or n1.category in [UnitCategory.FIRED_HEATERS, UnitCategory.FLARE_STACK]:
                for n2 in self.nodes:
                    if n2.is_fuel_source and n2 != n1:
                        dx = n1.coord_x - n2.coord_x
                        dy = n1.coord_y - n2.coord_y
                        dist = math.hypot(dx, dy)
                        if dist == 0 or dist > 120.0:
                            continue

                        align = (dx / dist) * wdx + (dy / dist) * wdy
                        if align > 0.707:
                            hazards.append(WindIgnitionHazard(
                                heater_node=n1,
                                fuel_node=n2,
                                distance=round(dist, 1),
                                hazard_type="Gas Ingestion / Upwind Siting Breach",
                                explanation=f"Ignition source {n1.tag} ({n1.category.value}) is downwind from {n2.tag} ({n2.category.value}) at distance {dist:.1f}m. Violates IPS-E-PR-190."
                            ))
        return hazards

    def import_from_csv(self, filepath: str) -> int:
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cat_str = row.get("Category", "").strip().upper()
                cat_enum = None
                for c in UnitCategory:
                    if c.name == cat_str or c.value == cat_str:
                        cat_enum = c
                        break
                if not cat_enum:
                    cat_enum = UnitCategory.UNFIRED_PROCESS_LOW_P

                tag = row.get("Tag", f"EQ-{count+1:02d}").strip()
                x = float(row.get("X", 0.0))
                y = float(row.get("Y", 0.0))
                z = float(row.get("Z", 0.0)) if row.get("Z") else 0.0
                radius = float(row.get("Radius", 6.0)) if row.get("Radius") else 6.0
                is_ign = row.get("IsIgnition", "").lower() in ["true", "1", "yes"]
                is_fuel = row.get("IsFuel", "").lower() in ["true", "1", "yes"]

                node = EquipmentNode(
                    tag=tag,
                    category=cat_enum,
                    coord_x=x,
                    coord_y=y,
                    elevation_z=z,
                    radius=radius,
                    is_ignition_source=is_ign,
                    is_fuel_source=is_fuel
                )
                self.add_node(node)
                count += 1
        return count

    def export_to_csv(self, filepath: str):
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tag", "Category", "X", "Y", "Z", "Radius", "IsIgnition", "IsFuel", "FlashPoint"])
            for n in self.nodes:
                writer.writerow([
                    n.tag,
                    n.category.value,
                    n.coord_x,
                    n.coord_y,
                    n.elevation_z,
                    n.radius,
                    n.is_ignition_source,
                    n.is_fuel_source,
                    n.flash_point or ""
                ])
