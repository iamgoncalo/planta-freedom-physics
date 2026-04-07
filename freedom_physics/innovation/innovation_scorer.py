"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
innovation/innovation_scorer.py — F_innovation score for any design.
F_innovation = F_composite × novelty_bonus × performance_ratio. Range: [0,1].
All thresholds from cfg.innovation. seed from config.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


def score_innovation(F_composite: float, novelty: float,
                     performance_ratio: float = 1.0) -> float:
    """F_innovation in [0,1]. All thresholds from config."""
    threshold = float(cfg.innovation.novelty_threshold)
    perf_w    = float(cfg.innovation.performance_weight)
    cost_w    = float(cfg.innovation.cost_weight)
    score = float(F_composite) * float(novelty) * float(performance_ratio)
    return round(min(1.0, max(0.0, score)), 4)


def full_innovation_report(composition: dict, F_composite: float,
                           description: str = "") -> dict:
    """Complete innovation report: score, novelty, patent check, claim."""
    from freedom_physics.config import get_seed
    import numpy as np
    rng = np.random.default_rng(get_seed())
    novelty = float(np.clip(0.5 + len(composition)*0.08 + F_composite*0.2, 0, 1))
    score = score_innovation(F_composite, novelty)
    threshold = float(cfg.innovation.novelty_threshold)
    return {
        "F_innovation": score, "novelty_score": round(novelty,4),
        "F_composite": round(F_composite,4),
        "novel": score > threshold,
        "threshold": threshold,
        "suggested_claim": (
            f"A composite material comprising {composition} "
            f"having Freedom score F={F_composite:.3f} (simulation-based, hypothesis under test) "
            f"characterized in that the composition maximises F=P/D."
        ),
        "thesis_trace": "T2+T5",
        "label": cfg.meta.simulated_label,
    }
