# SIMULATED — F=P/D HYPOTHESIS UNDER TEST · Zero hardcoding
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

economics/f_debt.py — Freedom-debt economic model.
F-debt = cost of sub-optimal conditions on human productivity.
Non-linear: (1-F)^1.5 — small deviations tolerated, large compound.
All params from config. SMN 2026 = €5.44/h.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'../..'))
from freedom_physics.config import cfg

def compute_fdbt(F: float, P_spatial: float, occupants: int,
                 area_m2: float, building_area_m2: float = 950.0) -> dict:
    econ = cfg.economics
    segs = econ.salary_segments
    employer_hourly = sum(
        float(getattr(segs,s).pct) * float(getattr(segs,s).employer_hourly)
        for s in vars(segs)
    )
    eps = float(getattr(cfg.economics,"epsilon",1e-14))
    exponent = float(getattr(cfg.economics,"fdbt_exponent",1.5))  # 1.5 from config
    relative_deficit = max(0.0, 1.0 - F / max(P_spatial, eps))
    comfort_impact   = relative_deficit ** exponent
    f_debt_h = comfort_impact * occupants * employer_hourly
    space_cost_h = (area_m2 / max(building_area_m2,eps)) * float(econ.rent_eur_m2_month) / 160
    space_waste_h = (1.0 - F) * space_cost_h
    return {
        "f_debt_eur_h":    round(f_debt_h, 4),
        "space_waste_eur_h": round(space_waste_h, 4),
        "total_eur_h":     round(f_debt_h + space_waste_h, 4),
        "comfort_impact":  round(comfort_impact, 4),
        "employer_hourly": round(employer_hourly, 4),
        "exponent":        exponent,
        "thesis":          "T2+T4",
        "label":           "SIMULATED. F=P/D HYPOTHESIS UNDER TEST."
    }