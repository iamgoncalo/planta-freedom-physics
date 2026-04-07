"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/transformer_physics.py — Transformer for F(t) trajectory prediction.
Context window from cfg.ml.transformer_context. seed from config.
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np


def predict_F_trajectory(history: list, steps_ahead: int = 10) -> dict:
    """Predict future F(t) from historical sequence. Numpy proxy."""
    rng  = np.random.default_rng(get_seed())
    ctx  = int(cfg.ml.transformer_context)
    hist = np.array(history[-ctx:])
    trend = float(np.polyfit(range(len(hist)), hist, 1)[0]) if len(hist) > 1 else 0.0
    last  = float(hist[-1]) if len(hist) > 0 else 0.5
    preds = []
    for i in range(steps_ahead):
        pred = float(np.clip(last + trend*(i+1) + rng.normal(0, 0.01), 0, 1))
        preds.append(round(pred, 4))
    return {"predictions": preds, "trend": round(trend, 6),
            "context_length": ctx, "thesis_trace": "T2",
            "label": cfg.meta.simulated_label}
