"""Generate parts_extra.yaml and supplier_strategic.yaml (run from repo root)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"

EXTRA_PARTS = [
    # steering & safety
    ("PART-STEERING-RACK", "Electric power steering rack", "chassis", "steering", 5, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS", "SUP-IN-BEARINGS"]),
    ("PART-STEERING-COL", "Steering column & intermediate shaft", "chassis", "steering", 4, "metals", "SUP-IN-STEEL", ["SUP-IN-STEEL", "SUP-IN-FORGING"]),
    ("PART-AIRBAG-ECU", "Airbag control unit & sensors", "safety", "passive_safety", 5, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS", "SUP-KR-SEMI"]),
    ("PART-AIRBAG-MOD", "Driver & passenger airbag modules", "safety", "passive_safety", 5, "plastics", "SUP-IN-STAMPING", ["SUP-IN-STAMPING", "SUP-JP-PARTS"]),
    ("PART-SEATBELT", "Seat belt retractor & buckle set", "safety", "passive_safety", 4, "metals", "SUP-IN-FASTENERS", ["SUP-IN-FASTENERS", "SUP-IN-SEATING"]),
    ("PART-ABS-MOD", "ABS / ESC hydraulic control module", "braking", "chassis_brakes", 5, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS", "SUP-IN-FRICTION"]),
    ("PART-EPB", "Electric parking brake actuator", "braking", "chassis_brakes", 4, "electronics", "SUP-IN-FRICTION", ["SUP-IN-FRICTION", "SUP-IN-ELEC"]),
    # powertrain extended
    ("PART-TURBO", "Turbocharger assembly (boosted petrol)", "powertrain", "engine", 4, "metals", "SUP-JP-POWERTRAIN", ["SUP-JP-POWERTRAIN", "SUP-IN-EXHAUST", "SUP-IN-FORGING"]),
    ("PART-INTERCOOLER", "Charge air cooler (intercooler)", "powertrain", "engine", 3, "metals", "SUP-IN-EXHAUST", ["SUP-IN-EXHAUST", "SUP-IN-STAMPING"]),
    ("PART-TIMING-BELT", "Timing belt / chain kit", "powertrain", "engine", 5, "rubber", "SUP-IN-CLUTCH", ["SUP-IN-CLUTCH", "SUP-JP-POWERTRAIN", "SUP-TH-RUBBER"]),
    ("PART-OIL-PUMP", "Engine oil pump module", "powertrain", "engine", 4, "metals", "SUP-IN-POWERTRAIN", ["SUP-IN-POWERTRAIN", "SUP-IN-FORGING"]),
    ("PART-WATER-PUMP", "Coolant water pump", "powertrain", "engine", 4, "metals", "SUP-IN-POWERTRAIN", ["SUP-IN-POWERTRAIN", "SUP-IN-HOSE"]),
    ("PART-RADIATOR", "Aluminium radiator core & tanks", "powertrain", "thermal", 4, "metals", "SUP-IN-CASTING", ["SUP-IN-CASTING", "SUP-IN-HOSE", "SUP-IN-AC"]),
    ("PART-COOLING-FAN", "Radiator cooling fan & shroud", "powertrain", "thermal", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-STAMPING"]),
    ("PART-CATALYST", "Catalytic converter & substrate", "powertrain", "emissions", 5, "metals", "SUP-IN-EXHAUST", ["SUP-IN-EXHAUST", "SUP-JP-PARTS"]),
    ("PART-MUFFLER", "Exhaust muffler & tailpipe", "powertrain", "emissions", 3, "metals", "SUP-IN-EXHAUST", ["SUP-IN-EXHAUST", "SUP-IN-STEEL"]),
    ("PART-FUEL-PUMP", "In-tank electric fuel pump module", "powertrain", "engine", 4, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-FILTERS"]),
    ("PART-THROTTLE", "Electronic throttle body", "powertrain", "engine", 4, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS"]),
    ("PART-ALTERNATOR", "Alternator 12V", "electrical", "electrical", 4, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-BATTERY"]),
    ("PART-STARTER", "Starter motor", "electrical", "electrical", 4, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-POWERTRAIN"]),
    ("PART-DRIVESHAFT", "Propshaft & CV joint assembly", "powertrain", "transmission", 4, "metals", "SUP-IN-FORGING", ["SUP-IN-FORGING", "SUP-IN-POWERTRAIN"]),
    ("PART-DIFF", "Differential & axle shaft", "powertrain", "transmission", 5, "metals", "SUP-IN-POWERTRAIN", ["SUP-IN-POWERTRAIN", "SUP-IN-FORGING", "SUP-IN-BEARINGS"]),
    ("PART-HUB-ASSY", "Wheel hub & bearing assembly", "chassis", "wheels_tires", 4, "metals", "SUP-IN-BEARINGS", ["SUP-IN-BEARINGS", "SUP-IN-STEEL"]),
    # EV
    ("PART-EV-MOTOR", "Traction electric motor", "electrical", "ev_powertrain", 5, "electronics", "SUP-KR-SEMI", ["SUP-KR-SEMI", "SUP-IN-EV-HARNESS", "SUP-JP-POWERTRAIN"]),
    ("PART-EV-INVERTER", "Power inverter module", "electrical", "ev_powertrain", 5, "semiconductors", "SUP-KR-SEMI", ["SUP-KR-SEMI", "SUP-IN-ELEC"]),
    ("PART-EV-OBC", "On-board charger (OBC)", "electrical", "ev_powertrain", 5, "electronics", "SUP-IN-EV-HARNESS", ["SUP-IN-EV-HARNESS", "SUP-KR-SEMI"]),
    ("PART-EV-DCDC", "DC-DC converter (12V auxiliary)", "electrical", "ev_powertrain", 4, "electronics", "SUP-IN-EV-HARNESS", ["SUP-IN-EV-HARNESS", "SUP-IN-ELEC"]),
    ("PART-BMS", "Battery management system (BMS)", "electrical", "ev_powertrain", 5, "semiconductors", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-KR-SEMI", "SUP-IN-BATTERY"]),
    # body & glass
    ("PART-WINDSHIELD", "Laminated windshield glass", "body", "body_glass", 4, "plastics", "SUP-IN-GLASS", ["SUP-IN-GLASS", "SUP-TH-RUBBER"]),
    ("PART-SIDE-GLASS", "Door & quarter glass set", "body", "body_glass", 3, "plastics", "SUP-IN-GLASS", ["SUP-IN-GLASS"]),
    ("PART-MIRROR", "Power ORVM assembly", "body", "body_exterior", 3, "electronics", "SUP-IN-LIGHTING", ["SUP-IN-LIGHTING", "SUP-IN-ELEC", "SUP-IN-GLASS"]),
    ("PART-BUMPER-F", "Front bumper fascia & absorber", "body", "body_exterior", 3, "plastics", "SUP-IN-PLASTICS", ["SUP-IN-PLASTICS", "SUP-IN-STAMPING"]),
    ("PART-BUMPER-R", "Rear bumper fascia", "body", "body_exterior", 3, "plastics", "SUP-IN-PLASTICS", ["SUP-IN-PLASTICS"]),
    ("PART-HOOD", "Bonnet (hood) panel", "body", "body_structure", 3, "metals", "SUP-IN-STEEL", ["SUP-IN-STEEL", "SUP-IN-STAMPING"]),
    ("PART-DOOR-OUTER", "Door outer panel (stamped)", "body", "body_structure", 3, "metals", "SUP-IN-STAMPING", ["SUP-IN-STAMPING", "SUP-IN-STEEL"]),
    ("PART-FUEL-TANK", "Plastic fuel tank module", "body", "fuel_system", 4, "plastics", "SUP-IN-PLASTICS", ["SUP-IN-PLASTICS", "SUP-IN-HOSE"]),
    ("PART-SUNROOF-ASSY", "Panoramic sunroof assembly", "body", "body_exterior", 3, "electronics", "SUP-IN-SUNROOF", ["SUP-IN-SUNROOF", "SUP-IN-GLASS"]),
    # lighting & ADAS
    ("PART-HEADLAMP", "LED headlamp unit", "electrical", "lighting", 4, "electronics", "SUP-IN-LIGHTING", ["SUP-IN-LIGHTING", "SUP-KR-SEMI", "SUP-IN-ELEC"]),
    ("PART-TAILLAMP", "LED tail lamp cluster", "electrical", "lighting", 3, "electronics", "SUP-IN-LIGHTING", ["SUP-IN-LIGHTING"]),
    ("PART-FOG-LAMP", "Fog lamp & DRL module", "electrical", "lighting", 2, "electronics", "SUP-IN-LIGHTING", ["SUP-IN-LIGHTING"]),
    ("PART-TPMS", "Tyre pressure monitoring sensors", "electrical", "adas", 3, "semiconductors", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS"]),
    ("PART-PARK-SENSOR", "Ultrasonic parking sensors", "electrical", "adas", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS"]),
    ("PART-REAR-CAM", "Rear view camera module", "electrical", "adas", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-KR-SEMI"]),
    ("PART-CLUSTER", "Digital instrument cluster", "electrical", "cockpit", 4, "semiconductors", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-KR-SEMI"]),
    ("PART-TELEMATICS", "Telematics control unit (TCU)", "electrical", "connectivity", 4, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-KR-SEMI"]),
    # comfort & interior
    ("PART-SEAT-FRONT", "Front seat frame & trim", "comfort", "interior", 3, "plastics", "SUP-IN-SEATING", ["SUP-IN-SEATING", "SUP-IN-STAMPING"]),
    ("PART-SEAT-REAR", "Rear seat assembly", "comfort", "interior", 2, "plastics", "SUP-IN-SEATING", ["SUP-IN-SEATING"]),
    ("PART-STEERING-WHL", "Steering wheel & airbag cover", "comfort", "cockpit", 3, "plastics", "SUP-IN-STAMPING", ["SUP-IN-STAMPING", "SUP-IN-SEATING"]),
    ("PART-AC-COMP", "AC compressor & condenser", "comfort", "thermal", 4, "electronics", "SUP-IN-AC", ["SUP-IN-AC", "SUP-IN-ELEC", "SUP-IN-HOSE"]),
    ("PART-CABIN-FILTER", "Cabin air filter element", "comfort", "thermal", 2, "plastics", "SUP-IN-FILTERS", ["SUP-IN-FILTERS", "SUP-IN-AC"]),
    ("PART-AIR-FILTER", "Engine air intake filter", "powertrain", "engine", 3, "plastics", "SUP-IN-FILTERS", ["SUP-IN-FILTERS", "SUP-TH-RUBBER"]),
    ("PART-OIL-FILTER", "Engine oil filter cartridge", "powertrain", "engine", 3, "metals", "SUP-IN-FILTERS", ["SUP-IN-FILTERS"]),
    ("PART-FUEL-FILTER", "Fuel filter module", "powertrain", "engine", 4, "plastics", "SUP-IN-FILTERS", ["SUP-IN-FILTERS", "SUP-IN-ELEC"]),
    ("PART-POWER-WINDOW", "Power window regulator & motor", "body", "body_electrical", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-STAMPING"]),
    ("PART-CENTRAL-LOCK", "Central locking & BCM", "electrical", "body_electrical", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-WIRING"]),
    ("PART-HORN", "Dual-tone horn set", "electrical", "body_electrical", 1, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC"]),
    ("PART-SPEAKER", "Door speaker & audio harness", "electrical", "cockpit", 2, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-IN-WIRING"]),
    ("PART-KEYFOB", "Smart key & immobilizer", "electrical", "security", 3, "electronics", "SUP-IN-ELEC", ["SUP-IN-ELEC", "SUP-JP-PARTS"]),
    # fluids & coatings
    ("PART-BRAKE-FLUID", "DOT brake fluid (factory fill)", "braking", "chassis_brakes", 3, "plastics", "SUP-IN-FRICTION", ["SUP-IN-FRICTION", "SUP-IN-HOSE"]),
    ("PART-COOLANT", "Long-life engine coolant", "powertrain", "thermal", 3, "plastics", "SUP-IN-HOSE", ["SUP-IN-HOSE", "SUP-IN-FILTERS"]),
    ("PART-PAINT-OEM", "OEM base & clear coat system", "body", "body_exterior", 3, "plastics", "SUP-IN-PAINT", ["SUP-IN-PAINT", "SUP-DE-METALS"]),
    ("PART-ADHESIVE", "Structural adhesives & sealants", "body", "body_sealing", 3, "plastics", "SUP-TH-RUBBER", ["SUP-TH-RUBBER", "SUP-IN-PLASTICS"]),
    ("PART-FASTENER-KIT", "Chassis & interior fastener kit", "chassis", "body_structure", 2, "metals", "SUP-IN-FASTENERS", ["SUP-IN-FASTENERS", "SUP-IN-STEEL"]),
    ("PART-TOOLING-DIE", "Progressive die & tooling (program)", "tooling", "manufacturing", 4, "metals", "SUP-IN-TOOLING", ["SUP-IN-TOOLING", "SUP-IN-STAMPING"]),
]

SOURCE_POOL = {
    "IN": ("https://www.acma.in/", "ACMA India"),
    "JP": ("https://www.globalsuzuki.com/", "Suzuki global"),
    "TH": ("https://www.irsg.info/", "International Rubber Study Group"),
    "MY": ("https://www.miti.gov.my/", "MITI Malaysia"),
    "DE": ("https://www.vda.de/en", "VDA Germany"),
    "KR": ("https://www.semiconductor.org/", "SIA semiconductors"),
}


def _bullet(text: str, country: str) -> dict:
    url, label = SOURCE_POOL.get(country, ("https://www.worldbank.org/", "World Bank"))
    return {"text": text, "source_url": url, "source_label": label}


def _supplier_strategic_entry(sid: str, name: str, country: str, commodities: list[str]) -> dict:
    comm = ", ".join(commodities[:2]) if commodities else "auto components"
    return {
        "id": sid,
        "name": name,
        "country": country,
        "swot": {
            "strengths": [
                _bullet(f"Established {comm} capability for Indian OEM programs", country),
                _bullet("ISO-quality systems and repeatability on volume SKUs", country),
            ],
            "weaknesses": [
                _bullet("Sub-tier visibility and working-capital dependency", country),
                _bullet("Lead-time stretch during port or monsoon disruptions", country),
            ],
            "opportunities": [
                _bullet("EV / hybrid content growth and export kit opportunities", country),
                _bullet("Localization incentives under Make-in-India component schemes", country),
            ],
            "threats": [
                _bullet("Commodity and FX volatility on input materials", country),
                _bullet("OEM dual-sourcing mandates reducing sole-source margin", country),
            ],
        },
        "pestle": {
            "political": [_bullet("Trade lane stability and import-duty exposure", country)],
            "economic": [_bullet("Steel, resin, and energy cost pass-through to MSIL", country)],
            "social": [_bullet("Skilled labor availability in manufacturing clusters", country)],
            "technological": [_bullet(f"EV-ready tooling for {comm}", country)],
            "legal": [_bullet("AIS / homologation and recall liability clauses", country)],
            "environmental": [_bullet("Scope 3 and recycled-content reporting pressure", country)],
        },
    }


def main() -> None:
    suppliers_raw = yaml.safe_load((CONFIG / "suppliers.yaml").read_text(encoding="utf-8"))
    suppliers = suppliers_raw.get("suppliers", [])

    extra = []
    for row in EXTRA_PARTS:
        pid, name, cat, vsys, crit, comm, primary, sids = row
        alt2 = sids[1] if len(sids) > 1 else primary
        alt = [
            f"Qualify {alt2} as overflow when {primary} risk exceeds threshold (split % from analysis, not fixed)",
            f"Emergency stock build at Manesar/Gurgaon for criticality {crit} SKU",
            "Homologation fast-track on ASEAN alternate if India port delays exceed 14 days",
        ]
        extra.append(
            {
                "id": pid,
                "name": name,
                "category": cat,
                "vehicle_system": vsys,
                "criticality": crit,
                "main_commodity": comm,
                "primary_supplier_id": primary,
                "supplier_ids": sids,
                "alternative_solutions": alt,
            }
        )

    (CONFIG / "parts_extra.yaml").write_text(
        yaml.dump({"parts": extra}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    strategic = {
        "disclaimer": "Demo SWOT & PESTLE per configured supplier — illustrative synthesis with public reference links.",
        "suppliers": [
            _supplier_strategic_entry(
                s["id"], s["name"], s["country"], s.get("commodities") or []
            )
            for s in suppliers
        ],
    }
    (CONFIG / "supplier_strategic.yaml").write_text(
        yaml.dump(strategic, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {len(extra)} extra parts, {len(strategic['suppliers'])} supplier strategic profiles")


if __name__ == "__main__":
    main()
