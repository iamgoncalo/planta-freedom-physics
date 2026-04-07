"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/innovation_agent.py — Innovation assessment. F_innovation + patent check.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

def assess_novelty(composition: dict, description: str = "") -> dict:
    rng = np.random.default_rng(get_seed())
    from freedom_physics.materials.material_freedom import composite_material_F
    F_s = composite_material_F(composition, "structural")["F_composite"]
    novelty = float(np.clip(0.5 + len(composition)*0.08 + F_s*0.2 + rng.uniform(-0.05,0.05), 0, 1))
    threshold = float(cfg.innovation.novelty_threshold)
    prior = [{"patent_id":f"EP{3000000+i}","similarity":round(float(rng.uniform(0.3,0.7)),3)}
             for i in range(2)]
    claim = (f"A composite material comprising {composition} having Freedom score F={F_s:.3f} "
             f"characterized in that the composition maximises F=P/D (hypothesis under test).")
    return {"composition": composition, "description": description,
            "novelty_score": round(novelty,4), "F_structural": round(F_s,4),
            "novel": novelty > threshold, "prior_art": prior,
            "suggested_claim": claim, "threshold": threshold,
            "label": cfg.meta.simulated_label}
