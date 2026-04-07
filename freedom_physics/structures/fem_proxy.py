"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
structures/fem_proxy.py — Freedom-FEM proxy. NOT real finite element method.
PROXY: structural F-field on simplified mesh. For demonstration only.
F_member = P_structure / D_member where D_member = stress/yield_strength.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_PROXY_LABEL = "PROXY — NOT real FEM. Freedom-FEM structural analog only."


def run_freedom_fem(area_m2: float, F_composite: float,
                    wall_thickness: float = 0.15) -> dict:
    """
    PROXY: structural Freedom-FEM on simplified floor plan.
    NOT real finite element analysis.
    F_member = P / D_member. Alert if F_member < cfg.building.fem_alert_threshold.
    """
    rng = np.random.default_rng(get_seed())
    threshold = float(cfg.building.fem_alert_threshold)
    n_members = 6
    members = []
    eps = float(getattr(cfg.economics,"epsilon",1e-14))
    for i in range(n_members):
        load = 0.6 + rng.uniform(0, 0.35)
        D_m  = load / max(F_composite, eps)
        F_m  = min(1.0, max(0.0, F_composite / D_m))
        members.append({"id": f"M{i+1}", "F": round(F_m,4),
                        "D": round(D_m,4), "load_factor": round(load,3),
                        "alert": F_m < threshold})
    F_struct = float(np.exp(np.mean([np.log(max(m["F"],eps)) for m in members])))
    weak = [m for m in members if m["alert"]]
    return {
        "F_structure": round(F_struct,4), "members": members,
        "weak_members": weak, "safety_ok": not weak,
        "threshold": threshold, "n_members": n_members,
        "proxy_label": _PROXY_LABEL,
        "thesis_trace": "T2+T5",
        "label": cfg.meta.simulated_label,
    }
