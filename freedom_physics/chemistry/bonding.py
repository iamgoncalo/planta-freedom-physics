"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
chemistry/bonding.py — Chemical bonds as D_bond crystallisation.
T2+T5: bond energy = D_bond. Stronger bond = higher D = lower F_bond.
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


# Bond energies (kJ/mol) — from NIST, used as D_bond proxy
_BOND_D = {
    "H-H": 436, "C-C": 347, "C=C": 614, "C≡C": 839,
    "C-H": 413, "C-O": 360, "C=O": 745, "O-H": 463,
    "N-N": 163, "N=N": 418, "N≡N": 945, "C-N": 305,
    "Si-Si": 222, "Si-O": 452, "Al-O": 512, "Fe-Fe": 118,
}
_MAX_D = max(_BOND_D.values())  # N≡N = 945


def bond_freedom(bond_type: str) -> dict:
    """F_bond = 1/D_bond_normalised. Strong bond = high D = low F. T2+T5."""
    D_val = _BOND_D.get(bond_type, 300)
    D_norm = D_val / _MAX_D  # normalised [0,1]
    F_bond = 1.0 / max(D_norm, 1e-14)
    F_bond = min(1.0, F_bond / (1.0/_MAX_D * _MAX_D))  # clip
    return {
        "bond_type": bond_type,
        "D_bond_kJ_mol": D_val,
        "D_bond_normalised": round(D_norm, 4),
        "F_bond": round(1.0 - D_norm, 4),  # F = 1-D_norm: weaker bond = higher F
        "interpretation": "Stronger bond = higher crystallised D = lower F_bond (T5)",
        "thesis_trace": "T2+T5",
        "label": cfg.meta.simulated_label,
    }


def bond_d_hierarchy() -> list:
    """All bonds sorted by D_bond (strongest = most crystallised D)."""
    results = [bond_freedom(b) for b in _BOND_D]
    return sorted(results, key=lambda x: x["D_bond_kJ_mol"], reverse=True)
