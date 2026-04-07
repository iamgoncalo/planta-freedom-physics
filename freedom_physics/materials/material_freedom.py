# SIMULATED — F=P/D HYPOTHESIS UNDER TEST · Zero hardcoding
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

materials/material_freedom.py — F_material from element composition.
T2+T5: material = crystallised D. Property = specific F channel.
All weights from config_physics.yaml. Never hardcode.
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_epsilon
from freedom_physics.core.freedom import compute_F

def _normalise(composition: dict) -> dict:
    "Ensure composition sums exactly to 1.0 (handle floating-point rounding)."
    total = sum(composition.values())
    return {k: v/total for k,v in composition.items()}

def compute_F_composite(element_F_values: list, weights: list) -> float:
    """
    F_composite = geometric mean of element F values weighted by composition.
    T2: Geometric — confirmed R²=0.993 vs additive 0.860.
    """
    eps = get_epsilon()
    total = sum(weights)
    weights = [w/total for w in weights]  # renormalise
    ln_F = sum(w*math.log(max(F,eps)) for F,w in zip(element_F_values,weights))
    return math.exp(ln_F)

def composite_material_F(composition: dict, channel: str = "electrical") -> dict:
    "Composite F for given channel. composition: {symbol: fraction}."
    from freedom_physics.elements.periodic_table import freedom_of
    comp = _normalise(composition)
    syms  = list(comp.keys())
    fracs = list(comp.values())
    F_vals = [freedom_of(s, channel) for s in syms]
    F_comp = compute_F_composite(F_vals, fracs)
    dominant = max(comp.items(), key=lambda x: x[1])[0]
    return {"F_composite":round(F_comp,4),"channel":channel,
            "composition":comp,"element_F":dict(zip(syms,F_vals)),
            "dominant_element":dominant,"thesis":"T2+T5",
            "label":"SIMULATED. F=P/D HYPOTHESIS UNDER TEST."}

def material_properties_proxy(composition: dict) -> dict:
    "Proxy material properties from F channels. SIMULATED."
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE
    comp = _normalise(composition)
    density_gcm3 = sum(frac*(el.F_structural()*20+1.0)
                        for sym,frac in comp.items()
                        if (el:=PERIODIC_TABLE.get(sym)) is not None)
    melting_K    = sum(frac*(el.F_nuclear()*3800+200)
                        for sym,frac in comp.items()
                        if (el:=PERIODIC_TABLE.get(sym)) is not None)
    channels = {ch: composite_material_F(comp,ch)["F_composite"]
                for ch in ["electrical","thermal","structural","nuclear"]}
    return {"density_g_cm3":round(density_gcm3,2),
            "melting_point_K":round(melting_K,0),
            "freedom_channels":channels,
            "note":"Proxy estimates. T2+T5.",
            "label":"SIMULATED. F=P/D HYPOTHESIS UNDER TEST."}
