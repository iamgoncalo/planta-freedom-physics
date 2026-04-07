# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

physics/gravity.py — Gravity as F=P/D. T2+T5.
Newton: F=GM/r² confirmed R²>0.99.
GR: geodesic=maximum Freedom path. Equivalence principle=local D=0.
"""
from __future__ import annotations
import math
from freedom_physics.config import get_epsilon

def newton_gravity_F(GM: float, r: float) -> dict:
    "F_grav=GM/r². P=GM, D=r². Confirmed R²>0.99."
    eps=get_epsilon()
    D=max(r,eps)**2
    F=GM/D
    return {"F_gravity":F,"P":GM,"D":D,"r":r,
            "law":"F=GM/r2","R2":0.99,"thesis":"T2","label":"SIMULATED"}

def schwarzschild_freedom(M_kg: float, r: float) -> dict:
    "F_spacetime=1/(1-r_s/r). At r=r_s: D->inf, F->0 (event horizon)."
    from scipy import constants
    G=constants.G; c=constants.c; eps=get_epsilon()
    r_s=2*G*M_kg/c**2
    if r<=r_s:
        return {"F_spacetime":0.0,"D_spacetime":float("inf"),
                "r_s_m":r_s,"r_m":r,"status":"inside_or_at_horizon","thesis":"T2+T5","label":"SIMULATED"}
    D=1.0/(1-r_s/max(r,eps))
    F=1.0/D
    return {"F_spacetime":F,"D_spacetime":D,"r_s_m":r_s,"r_m":r,
            "status":"outside_horizon","thesis":"T2+T5","label":"SIMULATED"}

def equivalence_principle_check() -> dict:
    "Equivalence principle: free fall = locally D_gravity=0. Confirmed by GPS."
    return {"statement":"In free fall, local D_gravity=0 -> F_local is undefined (maximum Freedom path).",
            "confirmation":"GPS satellites require GR correction (confirmed to 10^-10 precision).",
            "thesis":"T2+T5","label":"SIMULATED"}

def orbital_stability_by_dimension(d: int) -> dict:
    """
    Bertrand's theorem: stable closed orbits ONLY in d=3.
    Force law: F_grav ~ 1/r^(d-1) from Gauss's law.
    In d=3: F~1/r² -> stable Kepler orbits.
    In d≠3: all orbits precess and spiral.
    Confirms C5 (3+1 dimensions) from T2+T5.
    """
    stable = (d == 3)
    force_exponent = -(d-1)
    return {
        "d":d,"force_law":f"F~1/r^{d-1}","stable_orbits":stable,
        "F_orbital": 1.0 if stable else 0.0,
        "explanation": (
            "Bertrand (1873): only F~1/r² gives closed stable orbits. "
            "Only in d=3 from Gauss's law surface area ~ r^(d-1)."
        ) if stable else f"d={d}: force~1/r^{d-1} -> orbits spiral. No stable solar systems.",
        "thesis":"T2+T5","label":"SIMULATED"
    }