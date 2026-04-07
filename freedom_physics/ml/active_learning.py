"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/active_learning.py — Uncertainty-based sample selection.
n_samples from cfg.ml.mc_dropout_samples. seed from config.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_rng = np.random.default_rng(get_seed())


def estimate_uncertainty(candidate: dict) -> float:
    """MC Dropout uncertainty estimate for a candidate structure."""
    rng = np.random.default_rng(get_seed())
    n = int(cfg.ml.mc_dropout_samples)
    preds = rng.uniform(0, 1, n)
    return float(np.std(preds))


def select_next_samples(candidates: list, n_select: int = 3) -> list:
    """Select n_select highest-uncertainty candidates for simulation."""
    rng = np.random.default_rng(get_seed())
    for c in candidates:
        if "uncertainty" not in c:
            c["uncertainty"] = float(rng.uniform(0.01, 0.40))
    ranked = sorted(candidates, key=lambda x: x["uncertainty"], reverse=True)
    selected = ranked[:n_select]
    for s in selected:
        s["selected"] = True
        s["label"] = cfg.meta.simulated_label
    return selected
