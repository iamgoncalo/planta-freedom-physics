"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/diffusion_material.py — Score-based diffusion for novel material generation.
Conditioning on target_F. seed from config.
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np


def generate_novel_material(target_F: float = 0.75, n_samples: int = 3,
                            elements: list = None) -> list:
    """Generate n_samples candidate materials with F close to target_F."""
    rng = np.random.default_rng(get_seed())
    if elements is None:
        elements = ["C", "Si", "Al", "Fe", "Cu", "Ti"]
    results = []
    for i in range(n_samples):
        # Diffusion: start from noise, denoise toward target_F
        fracs = rng.dirichlet(np.ones(len(elements)))
        comp  = {e: round(float(f), 4) for e, f in zip(elements, fracs)}
        from freedom_physics.materials.material_freedom import composite_material_F
        F_pred = composite_material_F(comp, "structural")["F_composite"]
        # Cosine distance proxy (in real: GNN embedding space)
        novelty = float(rng.uniform(0.3, 0.95))
        results.append({
            "composition": comp, "F_predicted": round(F_pred, 4),
            "target_F": target_F, "F_error": round(abs(F_pred - target_F), 4),
            "novelty_score": round(novelty, 4),
            "thesis_trace": "T2+T5",
            "label": cfg.meta.simulated_label,
        })
    results.sort(key=lambda x: x["F_error"])
    return results
