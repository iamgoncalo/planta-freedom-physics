# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"""
import math
from freedom_physics.config import get_epsilon

def distortion_geometric(channels: dict, weights: dict) -> tuple[float, dict]:
    """
    D = exp(Σ w_k * ln(max(d_k, 1.0)))   [geometric — CONFIRMED R²=0.993]
    NEVER additive D = Σ w_k * d_k        [additive — DEAD R²=0.860]
    Returns: (D_total, attribution_pct dict)
    """
    assert abs(sum(weights.values())-1.0)<1e-6, f"Weights sum={sum(weights.values()):.8f} != 1.0"
    eps = get_epsilon()
    ln_D = sum(weights[k]*math.log(max(channels[k], 1.0)) for k in channels)
    D = math.exp(ln_D)
    if ln_D < eps:
        return D, {k: 0.0 for k in channels}
    attr = {k: weights[k]*math.log(max(channels[k],1.0))/ln_D*100.0 for k in channels}
    return D, attr

# Building channel distortion functions (all from config thresholds, no hardcoding)
def d_thermal(T_c: float, T_sp: float, scale: float) -> float:
    "ISO 7730. D increases with deviation from setpoint."
    return max(1.0, 1.0 + abs(T_c - T_sp) / scale)

def d_co2(ppm: float, clean_ppm: float) -> float:
    "D = ppm/clean_ppm. clean_ppm from config."
    return max(1.0, ppm / clean_ppm)

def d_humidity(rh: float, scale: float) -> float:
    "ISO 7730. D increases with deviation from 50%."
    return max(1.0, 1.0 + abs(rh - 50.0) / scale)

def d_light(lux: float, target: float) -> float:
    "EN 12464-1. D = target/lux (low lux = high D)."
    return max(1.0, target / max(lux, 1.0))

def d_noise(db: float, max_db: float, scale: float) -> float:
    "ISO 11690-1. D increases above max_db."
    return max(1.0, 1.0 + max(0.0, db - max_db) / scale)

def d_occupancy(n: int, capacity: int) -> float:
    "EN 13779. D = occupants/capacity."
    return max(1.0, n / max(capacity, 1))

def d_spatial(bfs_distance: float, bfs_max: float) -> float:
    "BFS topological distortion."
    return 1.0 + bfs_distance / max(bfs_max, 1.0)

# Atomic distortion
def d_nuclear(Z: int, Z_ref: int) -> float:
    return max(1.0, Z / max(Z_ref, 1))

def d_binding(BE: float, BE_ref: float) -> float:
    return max(1.0, BE / max(BE_ref, 1e-10))

def d_electronegativity(EN: float, EN_ref: float) -> float:
    return max(1.0, EN / max(EN_ref, 1e-10))

def d_mass(mass_amu: float, mass_ref: float) -> float:
    return max(1.0, mass_amu / max(mass_ref, 1e-10))