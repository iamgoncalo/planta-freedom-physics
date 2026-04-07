# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

swarm/pso.py — PSO setpoint optimisation. Friedman rank 1.1/5. T3.
"""
from __future__ import annotations
import numpy as np
from freedom_physics.config import cfg, get_seed

def run_PSO(fitness_fn, n_dims: int, lb: float | None=None, ub: float | None=None) -> dict:
    """Generic PSO minimiser. All params from config if not overridden."""
    import numpy as np
    from freedom_physics.config import cfg, get_seed
    swarm=getattr(cfg,'swarm',None)
    rng   = np.random.default_rng(get_seed())
    n_p   = int(getattr(swarm,'pso_particles',30))
    n_i   = int(getattr(swarm,'pso_iterations',100))
    w_val = float(getattr(swarm,'pso_inertia',0.729))
    c1    = float(getattr(swarm,'pso_c1',1.494))
    c2    = float(getattr(swarm,'pso_c2',1.494))
    _lb   = lb if lb is not None else float(getattr(swarm,'pso_search_T_min',0.0))
    _ub   = ub if ub is not None else float(getattr(swarm,'pso_search_T_max',1.0))
    pos   = rng.uniform(_lb, _ub, (n_p, n_dims))
    vel   = rng.uniform(-0.1, 0.1, (n_p, n_dims))
    pbest = pos.copy()
    pbest_f = np.array([fitness_fn(p) for p in pos])
    gbest   = pbest[np.argmin(pbest_f)].copy()
    gbest_f = float(pbest_f.min())
    for _ in range(n_i):
        r1,r2_arr = rng.random((n_p,n_dims)), rng.random((n_p,n_dims))
        vel = w_val*vel + c1*r1*(pbest-pos) + c2*r2_arr*(gbest-pos)
        pos = np.clip(pos+vel, _lb, _ub)
        curr_f = np.array([fitness_fn(p) for p in pos])
        upd = curr_f<pbest_f
        pbest[upd]=pos[upd]; pbest_f[upd]=curr_f[upd]
        if curr_f.min()<gbest_f:
            gbest_f=float(curr_f.min()); gbest=pos[np.argmin(curr_f)].copy()
    return {'best_x':gbest.tolist(),'best_f':gbest_f,'seed':get_seed(),
            'label':cfg.meta.simulated_label}

def pso_minimize(fn, bounds, **kw):
    """Alias for run_pso. Minimises fn subject to bounds."""
    return run_pso(fn, bounds, **kw)

def run_pso(fn, bounds, n_particles=None, n_iterations=None) -> dict:
    """Generic PSO minimiser. All params from config if not overridden."""
    import numpy as np
    from freedom_physics.config import cfg, get_seed
    rng = np.random.default_rng(get_seed())
    n_p = int(n_particles or cfg.swarm.pso_particles)
    n_i = int(n_iterations or cfg.swarm.pso_iterations)
    w   = float(cfg.swarm.pso_inertia)
    c1  = float(cfg.swarm.pso_c1)
    c2  = float(cfg.swarm.pso_c2)
    dim = len(bounds)
    lb  = np.array([b[0] for b in bounds])
    ub  = np.array([b[1] for b in bounds])
    pos = rng.uniform(lb, ub, (n_p, dim))
    vel = rng.uniform(-0.1, 0.1, (n_p, dim))
    pbest = pos.copy()
    pbest_f = np.array([fn(p) for p in pos])
    gbest = pbest[pbest_f.argmin()].copy()
    gbest_f = float(pbest_f.min())
    for _ in range(n_i):
        r1,r2 = rng.random((n_p,dim)),rng.random((n_p,dim))
        vel = w*vel + c1*r1*(pbest-pos) + c2*r2*(gbest-pos)
        pos = np.clip(pos+vel, lb, ub)
        curr_f = np.array([fn(p) for p in pos])
        upd = curr_f < pbest_f
        pbest[upd]=pos[upd]; pbest_f[upd]=curr_f[upd]
        if curr_f.min()<gbest_f: gbest_f=float(curr_f.min()); gbest=pos[curr_f.argmin()].copy()
    return {"best_x": gbest.tolist(), "best_f": gbest_f, "seed": get_seed(),
            "label": cfg.meta.simulated_label}
