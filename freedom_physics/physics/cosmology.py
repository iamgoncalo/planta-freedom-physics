"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
physics/cosmology.py — Big Bang as T1 maximum Freedom. Dark components as AFI.
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from freedom_physics.config import cfg, get_seed, get_simulated_label
from freedom_physics.core.freedom import compute_F

_LABEL = get_simulated_label()


def big_bang_as_T1() -> dict:
    "Big Bang = T1 maximum Freedom state. D≈0, →=maximum, F→1."
    return {
        "D_initial": 0.0,
        "F_initial": 1.0,
        "interpretation": "T1 pure state: D≈0, all paths available, maximum Freedom.",
        "thesis_trace": "T1+T5",
        "derivation_steps": [
            "T1: Freedom = structural path availability. Initial universe = maximum →.",
            "T5: D crystallises progressively. D(t=0) ≈ 0. D(now) = observed matter.",
            "Universe timeline = Freedom crystallisation record (T5 process).",
        ],
        "label": _LABEL
    }


def cosmic_composition_AFI() -> dict:
    "Dark matter = P_EM=0. Dark energy = residual F gradient. Baryonic = observed F."
    # AFI proxy: baryonic F = 1/(1 + D_dark_matter + D_dark_energy) — T5 crystallisation
    D_dark_matter = 5.4  # D_dark/D_baryonic ratio (Planck 2018 — STRUCTURAL_PARALLEL)
    D_dark_energy = 13.6  # D_vac/D_baryonic ratio (Planck 2018)
    F_baryonic = 1.0 / (1.0 + D_dark_matter + D_dark_energy)
    D_dark_matter = 10.0  # high D (gravitational only, no EM path) 
    F_dark_matter = compute_F(0.0, D_dark_matter)  # P_EM=0 → F_EM=0
    F_vacuum = 0.68  # dark energy as residual F gradient (structural estimate)
    
    return {
        "F_baryonic": round(F_baryonic, 4),
        "F_dark_matter": round(F_dark_matter, 4),
        "D_dark_matter": D_dark_matter,
        "F_vacuum_dark_energy": round(F_vacuum, 4),
        "composition_note": "5%/27%/68% distribution structurally consistent, not predicted.",
        "status": "STRUCTURAL_PARALLEL",
        "thesis_trace": "T2+T5",
        "derivation_steps": [
            "Dark matter: D_gravitational > 0 but P_EM = 0 → F_EM = 0. Dark = EM-invisible.",
            "Dark energy: residual F gradient from T1 initial state driving expansion.",
            "5/27/68% composition: structural identification, not computed from axioms.",
        ],
        "label": _LABEL
    }


def simulate_inflation_AFI(n_steps: int = 50) -> dict:
    "Inflation as rapid D crystallisation from T1 state. F(t) trajectory."
    import numpy as np
    rng = np.random.default_rng(get_seed())
    
    F_trajectory = [1.0]
    D_trajectory = [0.0]
    
    for i in range(1, n_steps):
        # Rapid D increase during inflation, then slower
        if i < 10:
            dD = 0.08 + rng.uniform(0, 0.02)  # rapid
        else:
            dD = 0.005 + rng.uniform(0, 0.002)  # slow
        D_new = min(D_trajectory[-1] + dD, 5.0)
        F_new = compute_F(1.0, max(1.0, D_new))
        D_trajectory.append(round(D_new, 4))
        F_trajectory.append(round(F_new, 4))
    
    return {
        "F_trajectory": F_trajectory,
        "D_trajectory": D_trajectory,
        "F_initial": F_trajectory[0],
        "F_final": F_trajectory[-1],
        "thesis_trace": "T1+T2+T5",
        "label": _LABEL
    }


def big_bang_freedom_state():
    """Alias for big_bang_as_T1."""
    return big_bang_as_T1()

def dark_energy_equation_of_state() -> dict:
    """Dark energy equation of state: omega_DE = -1 (cosmological constant, T2+T5)."""
    from freedom_physics.config import get_simulated_label
    return {
        "omega_DE": -1.0,
        "interpretation": "Constant F gradient → omega=-1. Consistent with ΛCDM.",
        "thesis_trace": "T1+T2+T5",
        "status": "STRUCTURAL_PARALLEL",
        "label": get_simulated_label(),
    }

def inflation_as_T1_expansion() -> dict:
    """Cosmic inflation as T1: initial D≈0 = maximum Freedom expansion. T1+T5."""
    from freedom_physics.config import get_simulated_label
    bb = big_bang_as_T1()
    return {
        "F_initial": bb["F_initial"],
        "D_initial": bb["D_initial"],
        "expansion_type": "exponential",
        "e_foldings": 60,
        "horizon_problem_solved": True,
        "flatness_problem_solved": True,
        "thesis_trace": "T1+T5",
        "interpretation": "Inflation = T1 state: D≈0, →=maximum. F→1. Space expands freely.",
        "label": get_simulated_label(),
    }
