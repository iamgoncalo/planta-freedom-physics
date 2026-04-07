"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
physics/fine_tuning.py — F_universe scan over physical constants.
Anthropic selection = F-maximisation selection (T2+T5).
thesis_trace: T2+T5
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import numpy as np
from freedom_physics.config import cfg, get_seed


def F_universe_from_constants(alpha: float, mass_ratio: float) -> float:
    """F_universe at given (alpha, mass_ratio). Peaks near observed values."""
    alpha_obs  = 1.0/137.036
    ratio_obs  = 1836.15
    F_em   = max(0.0, 1.0 - abs(math.log(max(alpha,1e-10)/alpha_obs))  / 3.0)
    F_mass = max(0.0, 1.0 - abs(math.log(max(mass_ratio,1e-10)/ratio_obs)) / 3.0)
    return (F_em * F_mass) ** 0.5


def scan_constant_space(n_alpha: int = 50, n_ratio: int = 50) -> dict:
    """Scan F_universe(alpha, m_e/m_p). Observed constants near F-maximum (T2+T5)."""
    rng = np.random.default_rng(get_seed())
    from scipy import constants as sc

    alpha_vals = np.linspace(1/300, 1/50, n_alpha)
    ratio_vals = np.linspace(200, 5000, n_ratio)

    F_grid = [[F_universe_from_constants(a, r) for r in ratio_vals] for a in alpha_vals]
    F_flat = [v for row in F_grid for v in row]

    obs_alpha = sc.alpha
    obs_ratio = sc.m_p / sc.m_e
    F_at_obs  = F_universe_from_constants(obs_alpha, obs_ratio)
    F_random  = float(np.mean(F_flat))

    steps = [
        "T2+T5: physical constants = D_crystallised values that maximise F_universe.",
        "Scan: F_universe(alpha, m_e/m_p) over realistic ranges.",
        f"F at observed constants = {F_at_obs:.4f}.",
        f"Mean F over scan = {F_random:.4f}.",
        "Anthropic selection = F-maximisation: observers exist where F_universe is high.",
        "Status: STRUCTURAL_PARALLEL — consistent, not predictive.",
    ]
    return {
        "observed_alpha": round(obs_alpha, 8),
        "observed_mass_ratio": round(obs_ratio, 2),
        "F_at_observed": round(F_at_obs, 4),
        "F_random_mean": round(F_random, 4),
        "F_above_random": F_at_obs > F_random,
        "thesis_trace": "T2+T5",
        "derivation_steps": steps,
        "status": "STRUCTURAL_PARALLEL",
        "label": cfg.meta.simulated_label,
    }
