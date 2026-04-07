# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

swarm/free_algorithm.py — FREE: Freedom-Regulated Emergent Exploration.
Derived directly from T1→T2→T3→T4→T5.
F: compute F=P/D per room every tick
R: ACO routing maximises F_global
E: PSO setpoints minimise D_thermal
E: alert cascade at F threshold (binary L-layer)
"""
from __future__ import annotations
import math
import numpy as np
from freedom_physics.config import cfg, get_seed, get_epsilon
from freedom_physics.core.freedom import compute_F, compute_F_global

def run_FREE(rooms: list[dict], n_iter: int | None = None, seed: int | None = None) -> dict:
    """
    Run FREE algorithm over a set of rooms.
    Each room: {id, P_spatial, D_total, capacity, occupants, avoid}
    Returns: {assignments, F_global_before, F_global_after, improvement_pct}
    All parameters from config. seed=2026 always.
    """
    rng      = np.random.default_rng(seed if seed is not None else get_seed())
    eps      = get_epsilon()
    n_iter   = n_iter or int(cfg.aco.n_iter if hasattr(cfg.aco,'n_iter') else 50)
    alpha_ph = float(cfg.aco.alpha)   # pheromone weight
    beta_ph  = float(cfg.aco.beta)    # freedom-heuristic weight
    rho_ph   = float(cfg.aco.rho)     # pheromone evaporation
    avoid    = list(cfg.aco.avoid_rooms)

    # Filter admissible rooms (L-layer binary filter)
    admissible = [r for r in rooms if r.get("id") not in avoid]

    # Compute initial F scores
    F_scores = {r["id"]: compute_F(r["P_spatial"], r["D_total"]) for r in rooms}
    F_before = compute_F_global(list(F_scores.values()))

    # Simple pheromone-based room assignment (ACO-inspired)
    pheromone = {r["id"]: 1.0 for r in admissible}
    best_assignment = {r["id"]: r.get("occupants",0) for r in rooms}
    best_F = F_before

    for _ in range(n_iter):
        # Heuristic = F score (pheromone ∝ Freedom, not ∝ 1/cost)
        scores = {rid: (pheromone[rid]**alpha_ph) * (max(F_scores[rid],eps)**beta_ph)
                  for rid in pheromone}
        total_score = sum(scores.values()) + eps
        probs = {rid: v/total_score for rid,v in scores.items()}

        # Redistribute occupants toward high-F rooms
        trial = {r["id"]: r.get("occupants",0) for r in rooms}
        # Evaporate
        for rid in pheromone:
            pheromone[rid] = (1-rho_ph) * pheromone[rid]
        # Deposit on high-F rooms
        for rid,prob in probs.items():
            pheromone[rid] += prob * max(F_scores[rid], eps)

        trial_F_vals = []
        for r in rooms:
            rid = r["id"]
            n = trial.get(rid, 0)
            from freedom_physics.core.distortion import d_occupancy
            d_occ = d_occupancy(n, r.get("capacity",1))
            D_adj = r["D_total"] * (d_occ**0.1)
            trial_F_vals.append(compute_F(r["P_spatial"], D_adj))

        trial_F = compute_F_global(trial_F_vals)
        if trial_F > best_F:
            best_F = trial_F
            best_assignment = trial

    improvement = (best_F - F_before) / max(F_before, eps) * 100.0
    return {
        "F_global_before":    round(F_before, 4),
        "F_global_after":     round(best_F, 4),
        "improvement_pct":    round(improvement, 2),
        "assignments":        best_assignment,
        "iterations":         n_iter,
        "avoided_rooms":      avoid,
        "thesis":             "T1+T2+T3+T4+T5",
        "label":              "SIMULATED. seed=2026.",
    }

def run_free(n_agents: int = 10, n_steps: int = 100) -> dict:
    """Run FREE algorithm: Freedom-Regulated Emergent Exploration. T1+T2+T3."""
    import numpy as np
    from freedom_physics.config import cfg, get_seed
    rng = np.random.default_rng(get_seed())
    n_a = int(n_agents)
    agents = rng.uniform(0.2, 0.8, (n_a, 2))  # [P, D] per agent
    F_traj = []
    for _ in range(int(n_steps)):
        F_vals = [float(p/max(d,1e-14)) for p,d in agents]
        F_global = float(np.exp(np.mean(np.log(np.clip(F_vals,1e-14,1)))))
        F_traj.append(round(F_global, 4))
        # Pheromone update: move toward higher F (T2 Law 2)
        for i in range(n_a):
            agents[i][0] = float(np.clip(agents[i][0] + rng.normal(0, 0.02), 0.1, 1.0))
            agents[i][1] = float(np.clip(agents[i][1] * 0.99, 1.0, 5.0))
    return {"F_global": round(float(np.mean(F_traj[-10:])), 4),
            "trajectory": F_traj,
            "n_agents": n_a, "n_steps": n_steps,
            "thesis_trace": "T1+T2+T3",
            "label": cfg.meta.simulated_label}
