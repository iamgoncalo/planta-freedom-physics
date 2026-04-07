"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/freedom_predictor.py — Predict F from structure before full simulation.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

def predict_F_from_structure(structure_features: dict) -> dict:
    from freedom_physics.ml.uncertainty_quantification import predict_with_uncertainty
    vals = list(structure_features.values()) if structure_features else [0.5]
    return predict_with_uncertainty(vals)
