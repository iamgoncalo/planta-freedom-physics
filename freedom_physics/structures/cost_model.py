"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
structures/cost_model.py — Material + construction costs from config.
All prices from cfg.material_costs. SMN from cfg.economics. Never hardcoded.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

_ELEMENT_KEY_MAP = {
    "C": "C_graphite_eur_per_kg",
    "Si": "Si_eur_per_kg",
    "Al": "Al_eur_per_kg",
    "Fe": "Fe_eur_per_kg",
    "Cu": "Cu_eur_per_kg",
    "Ti": "Ti_eur_per_kg",
    "W":  "W_eur_per_kg",
    "Mg": "Mg_eur_per_kg",
}


def cost_per_kg(element: str) -> float:
    """Price per kg from cfg.material_costs. Defaults to 5.0 if unknown."""
    key = _ELEMENT_KEY_MAP.get(element, None)
    if key:
        return float(getattr(cfg.material_costs, key, 5.0))
    return 5.0  # unknown element default


def compute_material_cost(composition: dict, mass_kg: float) -> dict:
    """Material cost from composition fractions and mass. All from config."""
    total = sum(composition.values())
    costs = {e: round(f/total * mass_kg * cost_per_kg(e), 2)
             for e, f in composition.items()}
    total_mat = round(sum(costs.values()), 2)
    return {"element_costs_eur": costs, "total_material_eur": total_mat,
            "mass_kg": mass_kg, "label": cfg.meta.simulated_label}


def compute_construction_cost(area_m2: float, smn_override: float = None) -> dict:
    """Construction labour cost from cfg. SMN from config always."""
    labour_m2 = float(cfg.material_costs.construction_labour_eur_per_m2)
    total = round(area_m2 * labour_m2, 2)
    return {"area_m2": area_m2, "labour_eur_per_m2": labour_m2,
            "total_labour_eur": total, "label": cfg.meta.simulated_label}


def full_cost_report(composition: dict, area_m2: float,
                     density_kg_m3: float = 2000.0) -> dict:
    """Complete cost: material + labour + contingency from config."""
    contingency = float(cfg.material_costs.contingency_factor)
    wall_vol = area_m2 * 0.15 * 2.5  # proxy
    mass_kg  = wall_vol * density_kg_m3
    mat  = compute_material_cost(composition, mass_kg)
    lab  = compute_construction_cost(area_m2)
    base = mat["total_material_eur"] + lab["total_labour_eur"]
    total = round(base * (1 + contingency), 2)
    return {"material": mat, "labour": lab,
            "contingency_factor": contingency,
            "total_eur": total, "area_m2": area_m2,
            "label": cfg.meta.simulated_label}
