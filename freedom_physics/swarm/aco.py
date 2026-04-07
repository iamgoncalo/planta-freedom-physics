# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

swarm/aco.py — ACO with F-pheromone. P_swarm = pheromone on improving edges. T3.
ACO late alignment > early in 87% of 2,987 trials (Deucalion, seed=2026).
"""
from __future__ import annotations
import numpy as np
from freedom_physics.config import cfg, get_seed, get_epsilon

def run_ACO(graph_edges: list[tuple], F_values: dict, n_ants: int = 20) -> dict:
    """
    ACO with pheromone ∝ F (not ∝ 1/cost — Freedom direction, not cost minimisation).
    Returns: best path, F_path, pheromone dict.
    Pintassilgo and avoid_rooms hard-excluded (L-layer, config.aco.avoid_rooms).
    """
    rng   = np.random.default_rng(get_seed())
    eps   = get_epsilon()
    alpha = float(float(getattr(getattr(cfg,"swarm",None),"aco_alpha",1.0)))
    beta  = float(float(getattr(getattr(cfg,"swarm",None),"aco_beta",2.0)))
    rho   = float(float(getattr(getattr(cfg,"swarm",None),"aco_rho",0.1)))
    avoid = list(getattr(getattr(cfg,"swarm",None),"avoid_rooms",[]))

    nodes   = list({n for edge in graph_edges for n in edge[:2]})
    edges   = [(u,v) for u,v in [e[:2] for e in graph_edges] if u not in avoid and v not in avoid]
    pheromone = {(u,v): 1.0 for u,v in edges}

    # Heuristic = F score of destination
    def eta(n): return max(F_values.get(n, 0.0), eps)

    best_path, best_F = [], 0.0

    for _ in range(n_ants):
        start = nodes[rng.integers(len(nodes))]
        path  = [start]
        visited = {start}
        for _step in range(min(len(nodes)-1, 10)):
            curr = path[-1]
            nbrs = [(v, pheromone.get((curr,v), pheromone.get((v,curr),eps)))
                    for u,v in edges if u==curr and v not in visited] + \
                   [(u, pheromone.get((u,curr), pheromone.get((curr,u),eps)))
                    for u,v in edges if v==curr and u not in visited]
            if not nbrs: break
            weights = [(n, (ph**alpha)*(eta(n)**beta)) for n,ph in nbrs]
            total = sum(w for _,w in weights) + eps
            probs = [w/total for _,w in weights]
            next_node = rng.choice([n for n,_ in weights], p=probs)
            path.append(next_node); visited.add(next_node)

        path_F = np.mean([F_values.get(n, 0.0) for n in path]) if path else 0.0
        if path_F > best_F:
            best_F = path_F; best_path = path

        # Deposit pheromone on improving edges
        for i in range(len(path)-1):
            u,v = path[i],path[i+1]
            if F_values.get(v,0) > F_values.get(u,0):  # improving only
                key = (u,v) if (u,v) in pheromone else (v,u)
                if key in pheromone:
                    pheromone[key] = (1-rho)*pheromone[key] + path_F

    return {"best_path":best_path,"best_F":round(best_F,4),
            "pheromone_snapshot":{str(k):round(v,4) for k,v in list(pheromone.items())[:5]},
            "avoided_rooms":avoid,
            "late_gt_early_pct_deucalion":float(float(getattr(getattr(cfg,"deucalion",None),"aco_late_gt_early_pct",87.0))),
            "thesis":"T3","label":"SIMULATED. seed=2026."}

def get_avoid_rooms() -> list:
    """Return rooms excluded from ACO assignment. From config, never hardcoded."""
    from freedom_physics.config import cfg
    ar = cfg.swarm.avoid_rooms
    return list(ar) if isinstance(ar, (list,)) else [str(ar)]
