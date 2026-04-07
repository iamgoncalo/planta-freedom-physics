"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
physics/quantum_gravity.py — Background independence from T1. Emergent metric.
F_global(N) peaks at N=3 (stable atomic orbits require 3+1 spacetime).
thesis_trace: T1+T4+T5
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


def compute_F_by_dimension(N: int) -> float:
    """F_global as function of spatial dimension N. Peaks at N=3."""
    from freedom_physics.core.constants_derivation import compute_F_by_dimension as _c
    return _c(N)


def emergent_metric_from_F(freedom_field: list, size: int = 3) -> dict:
    """
    T1+T5: Spacetime metric emerges from D-crystallisation field.
    Background independence: metric = output of F→L→R→Φ, not input.
    """
    import numpy as np
    rng = np.random.default_rng(int(cfg.meta.seed))
    n = size
    # g_mu_nu = delta_mu_nu * (1 + D_local) — D adds curvature
    g = np.eye(n+1)  # flat spacetime
    for i in range(min(n+1, len(freedom_field))):
        F_i = freedom_field[i]
        D_i = max(1.0, 1.0/max(F_i, 1e-14))
        g[i, i] = 1.0 + (D_i - 1.0) * 0.1  # perturbative curvature from D
    steps = [
        "T1: Freedom precedes spacetime. Metric is not background — it is output.",
        "T5: Each spacetime point has a local D-crystallisation value.",
        "Curvature: g_μν = η_μν × (1 + D_local × coupling) — perturbative.",
        "Background independence: F→L→R→Φ generates metric, not assumes it.",
    ]
    return {
        "metric_diagonal": [round(float(g[i,i]),6) for i in range(n+1)],
        "flat": all(abs(g[i,i]-1.0)<0.01 for i in range(n+1)),
        "thesis_trace": "T1+T4+T5",
        "derivation_steps": steps,
        "status": "STRUCTURAL_PARALLEL",
        "label": cfg.meta.simulated_label,
    }
