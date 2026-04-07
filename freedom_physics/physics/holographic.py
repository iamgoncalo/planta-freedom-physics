"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
physics/holographic.py — Holographic Principle from Intelligence Paradox (T4).
F_boundary > F_bulk for constrained volumes.
Bekenstein entropy as AFI boundary-bulk consequence.
thesis_trace: T4+T5
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


def compute_F_volume_vs_boundary(volume_size: float = 4.0) -> dict:
    """
    T4 Intelligence Paradox → information concentrates at boundary.
    F_boundary > F_bulk for all constrained volumes.
    """
    eps = 1e-14
    # Bulk: over-connected interior — Intelligence Paradox reduces F
    D_bulk = 1.0 + 0.5 * math.exp(-2.0 / max(volume_size, eps))
    P_bulk = 0.5  # bulk observer level
    F_bulk = P_bulk / D_bulk

    # Boundary: concentrated F, lower effective D (fewer paths but better quality)
    D_boundary = 1.0 + 0.2 * math.exp(-2.0 / max(volume_size, eps))
    P_boundary = 0.8
    F_boundary = P_boundary / D_boundary

    steps = [
        "T4: Intelligence Paradox — more bulk connections hurt efficiency.",
        "Bulk D increases with volume (over-connectivity → distortion).",
        "Boundary P higher (concentrated paths, lower effective D).",
        "Result: F_boundary > F_bulk for all constrained volumes.",
        "Bekenstein: S = A/4l_P² → all information on boundary = AFI consequence.",
    ]
    return {
        "volume_size": volume_size,
        "F_bulk":     round(F_bulk, 6),
        "F_boundary": round(F_boundary, 6),
        "D_bulk":     round(D_bulk, 6),
        "D_boundary": round(D_boundary, 6),
        "holographic_supported": F_boundary > F_bulk,
        "thesis_trace": "T4+T5",
        "derivation_steps": steps,
        "bekenstein_connection": "S=A/4l_P² recovered as STRUCTURAL_PARALLEL from T4",
        "label": cfg.meta.simulated_label,
    }


def bekenstein_entropy_AFI(area_m2: float) -> dict:
    """Bekenstein-Hawking entropy as boundary F concentration (T4)."""
    from scipy import constants as sc
    l_P = (sc.hbar * sc.G / sc.c**3)**0.5  # Planck length from constants
    S_bekenstein = area_m2 / (4 * l_P**2)  # in natural units
    # AFI: S = log(W) where W = number of boundary Freedom configurations
    F_boundary = 1.0 - math.exp(-area_m2 / (l_P**2 * 1e70))  # proxy
    return {
        "area_m2": area_m2,
        "S_bekenstein": S_bekenstein,
        "F_boundary": round(F_boundary, 6),
        "thesis_trace": "T4+T5",
        "status": "STRUCTURAL_PARALLEL",
        "label": cfg.meta.simulated_label,
    }
