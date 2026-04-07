"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/uncertainty_quantification.py — UQ for all simulation outputs.
Every prediction: {value, lower_95, upper_95, method}.
lower_95 <= value <= upper_95 always guaranteed.
n_samples from cfg.ml.mc_dropout_samples. seed from config.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np


def predict_with_uncertainty(x: list, method: str = None) -> dict:
    """Return {value, lower_95, upper_95, method}. Bounds guaranteed."""
    rng    = np.random.default_rng(get_seed())
    n      = int(cfg.ml.mc_dropout_samples)
    method = method or str(cfg.ml.uq_method)
    arr    = np.array(x, dtype=float)
    base   = float(np.clip(arr.mean(), 0, 1))
    # MC Dropout proxy: add noise
    samples = np.clip(base + rng.normal(0, 0.05, n), 0, 1)
    lo95   = float(np.percentile(samples, 2.5))
    hi95   = float(np.percentile(samples, 97.5))
    # Guarantee: lo95 <= base <= hi95
    lo95   = min(lo95, base)
    hi95   = max(hi95, base)
    return {"value": round(base, 4), "lower_95": round(lo95, 4),
            "upper_95": round(hi95, 4), "method": method,
            "n_samples": n, "thesis_trace": "T2",
            "label": cfg.meta.simulated_label}
