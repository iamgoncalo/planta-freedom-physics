"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
chemistry/reactions.py — Reaction direction from ∇F (gradient of Freedom).
T2 Law 2: systems evolve toward higher F (lower D, higher P).
Activation energy = D_barrier. Exothermic reactions: ΔD < 0 → ΔF > 0.
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


def reaction_direction(F_reactants: float, F_products: float) -> dict:
    """
    T2 Law 2: reaction proceeds if ΔF = F_products - F_reactants > 0.
    Direction from ∇F = gradient of Freedom in chemical space.
    """
    delta_F = F_products - F_reactants
    spontaneous = delta_F > 0
    return {
        "F_reactants": round(F_reactants, 4),
        "F_products":  round(F_products, 4),
        "delta_F":     round(delta_F, 4),
        "spontaneous": spontaneous,
        "direction":   "forward (→ products)" if spontaneous else "reverse (← reactants)",
        "interpretation": "ΔF>0: reaction increases Freedom = spontaneous. T2 Law 2.",
        "thesis_trace": "T2",
        "label": cfg.meta.simulated_label,
    }


def activation_barrier(F_reactants: float, D_barrier: float) -> dict:
    """
    D_barrier = activation energy distortion. Rate ∝ exp(-D_barrier).
    T2+T3: L-layer constraint gates the reaction path.
    """
    F_ts = max(0.0, F_reactants - D_barrier)  # transition state F
    rate_factor = math.exp(-D_barrier)
    return {
        "F_reactants": round(F_reactants, 4),
        "D_barrier":   round(D_barrier, 4),
        "F_transition_state": round(F_ts, 4),
        "rate_factor": round(rate_factor, 6),
        "thesis_trace": "T2+T3",
        "label": cfg.meta.simulated_label,
    }


def reaction_free_energy(delta_H_kJ: float, T_K: float, delta_S_J_K: float) -> dict:
    """
    ΔG = ΔH - TΔS recovered from F=P/D as: ΔF ∝ -ΔG.
    T2+T4: Gibbs free energy = negative of Freedom change.
    """
    delta_G = delta_H_kJ * 1000 - T_K * delta_S_J_K  # in J/mol
    delta_F_proxy = -delta_G / 1e6  # normalised proxy
    spontaneous = delta_G < 0
    return {
        "delta_H_kJ": delta_H_kJ, "T_K": T_K, "delta_S_J_K": delta_S_J_K,
        "delta_G_J": round(delta_G, 2),
        "spontaneous": spontaneous,
        "delta_F_proxy": round(delta_F_proxy, 6),
        "interpretation": "ΔG<0 = ΔF>0: Gibbs spontaneity = AFI direction. T2+T4.",
        "thesis_trace": "T2+T4",
        "label": cfg.meta.simulated_label,
    }
