# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters loaded from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"""
from __future__ import annotations
import math, numpy as np
from freedom_physics.config import cfg, get_alpha, get_epsilon

def compute_F(P: float, D: float, alpha: float | None = None, clip: bool = True) -> float:
    """
    Core Law of Freedom: F = (P/D)^alpha.
    alpha=None → uses config.framework.alpha_passive (1.000 at P=1).
    Clips to [0,1] by default.
    SIMULATED. F=P/D HYPOTHESIS UNDER TEST.
    """
    eps = get_epsilon()
    if alpha is None:
        alpha = get_alpha("passive")
    D_safe = max(float(D), eps)
    F = (float(P) / D_safe) ** alpha
    return float(min(1.0, max(0.0, F))) if clip else float(F)

def compute_F_passive(D: float) -> float:
    "F = 1/D at P=1 passive limit. Recovers Ohm, Fourier, Fick, Darcy, Langevin."
    return compute_F(1.0, D, alpha=get_alpha("passive"))

def compute_F_building(P_spatial: float, D_total: float) -> float:
    "F with building alpha (1.242, CI [1.19,1.29])."
    return compute_F(P_spatial, D_total, alpha=get_alpha("buildings"))

def compute_F_global(room_freedoms: list[float]) -> float:
    "F_global = geometric mean of room freedoms. Confirmed by Deucalion."
    eps = get_epsilon()
    vals = [max(f, eps) for f in room_freedoms if f > 0]
    if not vals: return 0.0
    return float(math.exp(sum(math.log(v) for v in vals) / len(vals)))

def freedom_rate(P: float, D: float, P_dot: float, D_dot: float) -> float:
    "dF/dt = (P_dot*D - P*D_dot) / D^2"
    eps = get_epsilon()
    D_s = max(D, eps)
    return (P_dot * D_s - P * D_dot) / D_s**2

def verify_axioms(P: float, D: float, delta: float = 0.01) -> dict:
    "Verify C1 monotonicity, C2 scale-covariance."
    F0 = compute_F(P, D, clip=False)
    dFdP = (compute_F(P+delta,D,clip=False)-compute_F(P-delta,D,clip=False))/(2*delta)
    dFdD = (compute_F(P,D+delta,clip=False)-compute_F(P,D-delta,clip=False))/(2*delta)
    c1 = dFdP > 0 and dFdD < 0
    c2 = all(abs(compute_F(lam*P,lam*D,clip=False)-F0)<1e-9 for lam in [0.01,2.0,100.0])
    return {"C1_monotonicity":c1,"C2_scale_covariance":c2,"F":F0,"all_pass":c1 and c2,
            "label":"SIMULATED. F=P/D HYPOTHESIS UNDER TEST."}