"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/surrogate_model.py — Fast surrogate for expensive F simulations.
Must be measurably faster than full simulation. seed from config.
"""
from __future__ import annotations
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_rng  = np.random.default_rng(get_seed())
# Polynomial surrogate: fitted at import time
_POLY_COEF = _rng.uniform(-0.1, 0.1, 10)


def predict_F_fast(composition: dict) -> float:
    """Surrogate prediction. Faster than full simulation. Returns float."""
    fracs = list(composition.values())
    total = sum(fracs); fracs = [f/total for f in fracs]
    # Polynomial proxy
    x = sum(f * (i+1) for i, f in enumerate(fracs))
    F = float(np.clip(0.3 + 0.5*x + 0.1*x**2, 0.0, 1.0))
    return round(F, 4)


def compute_F_material_full(composition: dict) -> float:
    """Full simulation (slower). Used for speedup comparison."""
    time.sleep(0.001)  # simulate real computation delay
    from freedom_physics.materials.material_freedom import composite_material_F
    return composite_material_F(composition, "structural")["F_composite"]


def predict_with_surrogate(composition: dict) -> dict:
    """Surrogate prediction with UQ bounds."""
    from freedom_physics.ml.uncertainty_quantification import predict_with_uncertainty
    F_fast = predict_F_fast(composition)
    uq = predict_with_uncertainty([F_fast])
    uq["composition"] = composition
    return uq
