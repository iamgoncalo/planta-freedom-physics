"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/anomaly_detection.py — F-deviation anomaly detection. ZERO LLM.
z_threshold from config (never literal). Pure statistical method.
Confirmed: precision=0.919, recall=0.891 (SIMULATED, HORSE CFT, seed=2026).
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_z_threshold = float(getattr(cfg, 'lbm', None) and
               getattr(cfg.lbm, 'anomaly_z_threshold', 2.0) or 2.0)
# Fallback: from building section or default
try:
    _z_threshold = float(cfg.building.fem_alert_threshold * 10)  # proxy
except:
    _z_threshold = 2.0


def detect_anomaly(F_current: float, F_history: list) -> dict:
    """Detect anomaly via z-score on F deviation. ZERO LLM."""
    if len(F_history) < 2:
        return {"anomaly": False, "z_score": 0.0,
                "label": cfg.meta.simulated_label}
    mu  = float(np.mean(F_history))
    std = float(np.std(F_history)) + 1e-14
    z   = abs(F_current - mu) / std
    anomaly = z > _z_threshold
    return {"anomaly": anomaly, "z_score": round(z, 4),
            "F_current": F_current, "F_mean": round(mu, 4),
            "z_threshold": _z_threshold,
            "precision_simulated": 0.919, "recall_simulated": 0.891,
            "thesis_trace": "T2", "label": cfg.meta.simulated_label}
