# SIMULATED — F=P/D HYPOTHESIS UNDER TEST · Zero hardcoding
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

materials/alloys.py — PSO-optimised alloy composition.
Target: maximise F_composite for given property channel.
All hyperparams from config. seed=2026.
"""
from __future__ import annotations
import math, sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'../..'))
from freedom_physics.config import cfg, get_seed
from freedom_physics.materials.material_freedom import compute_F_composite
from freedom_physics.elements.periodic_table import freedom_of

def optimise_alloy_pso(elements: list[str], channel: str = "electrical",
                       budget_per_kg_eur: float | None = None) -> dict:
    """
    PSO over composition fractions of `elements` to maximise F_composite[channel].
    Returns: {best_composition, F_composite, iterations, seed, label}
    """
    rng     = np.random.default_rng(get_seed())
    n_p     = int(cfg.swarm.pso_particles)
    n_iter  = int(cfg.swarm.pso_iterations)
    w       = float(cfg.swarm.pso_inertia)
    c1      = float(cfg.swarm.pso_c1)
    c2      = float(cfg.swarm.pso_c2)
    n       = len(elements)
    F_els   = np.array([freedom_of(s, channel) for s in elements])

    def fitness(fracs):
        f = np.abs(fracs); f = f/f.sum()
        return compute_F_composite(F_els.tolist(), f.tolist())

    # Initialise: simplex-sampled fractions
    pos  = rng.dirichlet(np.ones(n), n_p)
    vel  = rng.uniform(-0.1, 0.1, (n_p, n))
    pbest   = pos.copy()
    pbest_f = np.array([fitness(p) for p in pos])
    gbest   = pbest[pbest_f.argmax()].copy()
    gbest_f = float(pbest_f.max())

    for _ in range(n_iter):
        r1, r2 = rng.random((n_p,n)), rng.random((n_p,n))
        vel  = w*vel + c1*r1*(pbest-pos) + c2*r2*(gbest-pos)
        pos  = pos + vel
        # Project to simplex
        for i in range(n_p):
            p = np.abs(pos[i]); pos[i] = p/p.sum()
        curr_f = np.array([fitness(p) for p in pos])
        upd    = curr_f > pbest_f
        pbest[upd] = pos[upd]; pbest_f[upd] = curr_f[upd]
        if curr_f.max() > gbest_f:
            gbest_f = float(curr_f.max()); gbest = pos[curr_f.argmax()].copy()

    best_comp = {e: round(float(v),4) for e,v in zip(elements,gbest)}
    return {"best_composition":best_comp,"F_composite":round(gbest_f,4),
            "channel":channel,"n_iterations":n_iter,"seed":get_seed(),
            "element_F":{e:round(float(f),4) for e,f in zip(elements,F_els)},
            "thesis":"T2+T3","label":"SIMULATED. F=P/D HYPOTHESIS UNDER TEST."}