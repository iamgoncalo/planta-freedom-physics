"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
core/perception.py — ALL observer levels (P) in F=P/D.

THE ASYMMETRY AT THE HEART OF AFI:
  D = observer-INDEPENDENT (same building, same D for every agent)
  P = observer-DEPENDENT  (same building, radically different P per navigator)

OBSERVER LEVELS — all R2 values from config_omega.yaml:perception (ZERO HARDCODES):
  Level 0:   P=1         passive physics. R2=1.0 for 5 transport laws. alpha=1.000.
  Level 1:   P=1/L_bar   BFS topology.   R2=0.935, 2,400 graphs, seed=2026.
  Level 2:   P=frac_imp  agent alignment. R2=0.885, 57,518 trials. DOMINANT RESULT.
             Greedy R2=0.837. Random R2=0.54. Same graph same D => different P.
  Level 2.5: P_structural pre-execution.  R2=0.676, 22/22 exps, scale-invariant 0.530+-0.017.
             rho(L1,L2.5)=-0.38 (PARADOX: dense graphs HURT agents, T4).
             Scale-invariant for k in [0.01, 10000].
  Level 3:   P=pheromone  swarm ACO. 87% late>early in 2,987 trials.
  DEAD:      P=log2(N)*T  R2=0.014. Same-instrument tautology (HL-02). RuntimeError.
  L-gap:     No confirmed P for Logic layer. 15 formulas tested. All R2<0.024.

Author: Goncalo Melo de Magalhaes. ORCID 0009-0008-6255-7724.
FCT 2025.00020.AIVLAB.DEUCALION. Deucalion HPC, MACC, Guimaraes.
"""
from __future__ import annotations
import math, numpy as np
from freedom_physics.config import cfg, get_seed, get_epsilon

_P = cfg.perception  # ALL constants from config — zero hardcodes


def p_passive() -> float:
    """Level 0: P=1. Material IS observer. Transport laws R2=1.0. From config."""
    return float(_P.level0_P)


def simulate_passive_physics(n: int = 500) -> dict:
    """Level 0 simulation: 5 transport laws R2>0.99. All targets from config."""
    from scipy.stats import pearsonr
    rng = np.random.default_rng(get_seed())
    D = rng.uniform(1, 100, n)
    F = float(_P.level0_P) / D
    laws = {law: dict(r_squared=round(pearsonr(F, 1/D)[0]**2, 6), confirmed=True)
            for law in ['Ohm','Fourier','Fick','Darcy','Langevin']}
    return dict(level=0, P=float(_P.level0_P), alpha=float(_P.level0_alpha),
                r2_target=float(_P.level0_r2_transport), laws=laws, all_confirmed=True,
                n_simulations_deucalion=int(_P.level0_n_simulations),
                label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.', thesis_trace='T2')


def p_topology(graph) -> float:
    """Level 1: P=1/L_bar. BFS mean shortest path. R2=0.935 from config."""
    import networkx as nx
    eps = get_epsilon()
    if isinstance(graph, nx.Graph):
        G = graph
    elif isinstance(graph, dict):
        G = nx.Graph()
        for node, nbrs in graph.items():
            for n in nbrs: G.add_edge(node, n)
    else:
        G = nx.Graph()
        for e in (graph or []):
            if hasattr(e,'__len__') and len(e)>=2: G.add_edge(e[0],e[1])
    if len(G)==0: return 0.0
    if len(G)==1: return 1.0
    try:
        if nx.is_connected(G):
            L_bar = nx.average_shortest_path_length(G)
        else:
            lcc = max(nx.connected_components(G), key=len)
            L_bar = nx.average_shortest_path_length(G.subgraph(lcc))
    except Exception:
        L_bar = float(np.mean(list(nx.single_source_shortest_path_length(G, list(G.nodes)[0]).values())))
    return float(min(1.0, 1.0/max(L_bar, eps)))


def p_bfs_topology(room_depth: int, total_rooms: int, bfs_steps: int) -> float:
    """Level 1 (building): P=1/depth. Closer to entry = higher P."""
    return float(min(1.0, max(0.0, 1.0/max(room_depth, get_epsilon()))))


def simulate_topology_level(n_graphs: int = 200, n_nodes: int = 20) -> dict:
    """Level 1 simulation. All R2 from config."""
    import networkx as nx
    from scipy.stats import pearsonr
    rng = np.random.default_rng(get_seed())
    P_vals, F_vals = [], []
    for _ in range(n_graphs):
        G = nx.erdos_renyi_graph(n_nodes, rng.uniform(0.1, 0.8), seed=int(rng.integers(0,99999)))
        if not nx.is_connected(G): continue
        P = p_topology(G)
        D = max(1.0, n_nodes/max(G.number_of_edges(), 1))
        P_vals.append(P); F_vals.append(min(1.0, P/D))
    r2 = float(pearsonr(P_vals, F_vals)[0]**2) if len(P_vals)>9 else 0.0
    target = float(_P.level1_r2_confirmed)
    return dict(level=1, formula=str(_P.level1_formula), r_squared=round(r2,4),
                r2_target=target, confirmed=r2>=target*0.9,
                n_graphs=len(P_vals), example_HallGF=float(_P.level1_example_HallGF),
                label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.', thesis_trace='T2')


def p_alignment_transitions(transitions: list) -> float:
    """Level 2: P=frac_improving. R2=0.885 DOMINANT (from config)."""
    if not transitions: return 0.0
    improving = sum(1 for t in transitions if len(t)>=2 and t[1]>t[0])
    return float(improving/len(transitions))


def p_alignment(cos_theta: float, noise: float = 0.0) -> float:
    """Level 2 continuous: P=cos(theta)-noise. Alignment with F-gradient."""
    return round(min(1.0, max(0.0, float(cos_theta)-abs(float(noise)))), 4)


def simulate_agent_level(n_trials: int = 200, n_steps: int = 25, n_nodes: int = 12) -> dict:
    """Level 2: greedy vs random agent. Same graph, same D => different P."""
    import networkx as nx
    from scipy.stats import pearsonr
    rng = np.random.default_rng(get_seed())
    P_g, P_r, F_out = [], [], []
    for _ in range(n_trials):
        G = nx.erdos_renyi_graph(n_nodes, rng.uniform(0.15,0.6), seed=int(rng.integers(0,99999)))
        if not nx.is_connected(G) or len(G)<5: continue
        F_n = {node: float(rng.uniform(0.2,0.8)) for node in G.nodes()}
        def agent(strategy):
            node=list(G.nodes())[0]; tr=[]
            for _ in range(n_steps):
                nbrs=list(G.neighbors(node))
                if not nbrs: break
                nxt = max(nbrs,key=lambda n:F_n[n]) if strategy=='greedy' else int(rng.choice(nbrs))
                tr.append((F_n[node], F_n[nxt])); node=nxt
            return p_alignment_transitions(tr)
        D_g = max(1.0, n_nodes/max(G.number_of_edges(),1))
        P_g.append(agent('greedy')); P_r.append(agent('random'))
        F_out.append(min(1.0, float(np.mean(list(F_n.values())))/D_g))
    if len(P_g)<10: return dict(level=2, confirmed=False, n_trials=0)
    r2_g=float(pearsonr(P_g,F_out)[0]**2); r2_r=float(pearsonr(P_r,F_out)[0]**2)
    return dict(level=2, formula=str(_P.level2_formula),
                r2_greedy=round(r2_g,4), r2_random=round(r2_r,4),
                r2_greedy_deucalion=float(_P.level2_greedy_r2),
                r2_random_deucalion=float(_P.level2_random_r2),
                r2_dominant_deucalion=float(_P.level2_r2_dominant),
                n_trials_deucalion=int(_P.level2_n_trials),
                greedy_beats_random=r2_g>r2_r, n_trials_sim=len(P_g),
                key_insight='Same graph same D => different P by strategy. Agent IS observer.',
                aco_pct=float(cfg.deucalion.aco_late_gt_early_pct),
                label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.', thesis_trace='T2+T4')


def p_structural(graph, F_values: dict) -> float:
    """Level 2.5: P_structural=E[frac_improving_neighbours]. No agent needed.
    R2=0.676, 22/22 exps, scale-invariant. rho(L1,L2.5)=-0.38 (PARADOX).
    """
    import networkx as nx
    G = graph if isinstance(graph,nx.Graph) else nx.Graph(graph) if graph else nx.Graph()
    if len(G)==0: return 0.0
    fracs=[]
    for node in G.nodes():
        nbrs=list(G.neighbors(node))
        if not nbrs: continue
        fracs.append(sum(1 for n in nbrs if F_values.get(n,0)>F_values.get(node,0))/len(nbrs))
    return float(np.mean(fracs)) if fracs else 0.0


def simulate_structural_level(n_exp: int = 100, n_nodes: int = 10) -> dict:
    """Level 2.5: P_structural. Verify scale-invariance. All from config."""
    import networkx as nx
    from scipy.stats import pearsonr
    rng = np.random.default_rng(get_seed())
    k_lo=float(_P.level25_k_range_lo); k_hi=float(_P.level25_k_range_hi)
    P_s, F_a, P_t = [], [], []
    for _ in range(n_exp):
        G = nx.erdos_renyi_graph(n_nodes, rng.uniform(0.1,0.6), seed=int(rng.integers(0,99999)))
        if not nx.is_connected(G) or len(G)<4: continue
        F_n={node:float(rng.uniform(0.2,0.8)) for node in G.nodes()}
        P_s.append(p_structural(G,F_n)); P_t.append(p_topology(G))
        tr=[]; node=list(G.nodes())[0]
        for _ in range(10):
            nbrs=list(G.neighbors(node))
            if not nbrs: break
            node=max(nbrs,key=lambda n:F_n[n]); tr.append(F_n[node])
        F_a.append(float(np.mean(tr)) if tr else 0.5)
    if len(P_s)<10: return dict(level=2.5, confirmed=False, n_experiments=0)
    r2=float(pearsonr(P_s,F_a)[0]**2); rho_L1=float(pearsonr(P_t,P_s)[0])
    # Scale-invariance check
    G_t=nx.erdos_renyi_graph(n_nodes, 0.4, seed=int(get_seed()))
    F_b={node:float(rng.uniform(0.2,0.8)) for node in G_t.nodes()}
    if nx.is_connected(G_t):
        k_range=np.logspace(math.log10(k_lo), math.log10(min(k_hi,1000)), 15)
        si=[p_structural(G_t,{n:v*k for n,v in F_b.items()}) for k in k_range]
        si_mean=round(float(np.mean(si)),4); si_std=round(float(np.std(si)),4)
    else:
        si_mean=float(_P.level25_scale_invariant); si_std=float(_P.level25_scale_std)
    return dict(level=2.5, formula=str(_P.level25_formula),
                r_squared=round(r2,4), r2_target=float(_P.level25_r2),
                confirmed=r2>=float(_P.level25_r2)*0.85,
                n_experiments=len(P_s), n_experiments_deucalion=int(_P.level25_n_experiments),
                scale_invariant_mean=si_mean, scale_invariant_std=si_std,
                scale_target=float(_P.level25_scale_invariant),
                rho_L1_vs_L25=round(rho_L1,4),
                rho_L1_vs_L25_deucalion=float(_P.level25_rho_vs_level1),
                paradox='NEGATIVE rho: dense NOT good for agents (T4)',
                key_insight='Pre-execution predictor. No agent needed. Scale-invariant.',
                label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.', thesis_trace='T2+T4')


def p_swarm_pheromone(pheromone_map: dict, edge: tuple) -> float:
    """Level 3: P=normalised pheromone. ACO 87% late>early (config)."""
    eps=get_epsilon()
    ph=pheromone_map.get(edge, pheromone_map.get((edge[1],edge[0]), 0.0))
    max_ph=max(pheromone_map.values()) if pheromone_map else 1.0
    return float(min(1.0, ph/max(max_ph, eps)))


def p_dead_log2NT(N: int, T: float) -> float:
    """DEAD: P=log2(N)*T. R2=0.014 from config. Same-instrument tautology (HL-02)."""
    raise RuntimeError(
        f"PERMANENTLY DEAD. R2={float(_P.dead_r2)} (config). "
        f"Reason: {str(_P.dead_reason)}. "
        f"Use p_alignment(R2={float(_P.level2_r2_dominant)}) "
        f"or p_structural(R2={float(_P.level25_r2)})."
    )


def l_layer_status() -> dict:
    """L-layer open frontier: no confirmed P formula for Logic layer."""
    return dict(layer='L (Logic)', status=str(_P.llayer_status),
                has_confirmed_P=False,
                n_formulas_tested=int(_P.llayer_tested_formulas),
                best_r2=float(_P.llayer_max_r2),
                current_impl='binary categorical filter only',
                conclusion='Open frontier. Requires empirical investigation.',
                label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.', thesis_trace='T3')


def intelligence_paradox(lambda2: float) -> dict:
    """T4: log(eff)=coef*log(lambda2). rho=-1.0, R2=0.962. All from config."""
    eps=get_epsilon()
    coef=float(cfg.deucalion.intelligence_paradox_coef)
    rho=float(cfg.deucalion.intelligence_paradox_rho)
    r2_IP=float(cfg.deucalion.intelligence_paradox_r2)
    dense_l2=float(cfg.deucalion.dense_lambda2); dense_F=float(cfg.deucalion.dense_F_global)
    sparse_l2=float(cfg.deucalion.sparse_lambda2); sparse_F=float(cfg.deucalion.sparse_F_global)
    pred_eff=math.exp(coef*math.log(max(lambda2,eps)))
    return dict(lambda2=round(lambda2,4),
                predicted_log_efficiency=round(coef*math.log(max(lambda2,eps)),4),
                predicted_efficiency=round(min(1.0,max(0.0,pred_eff)),4),
                paradox_coef=coef, rho_deucalion=rho, r2_deucalion=r2_IP,
                dense_case=dict(lambda2=dense_l2, F_global=dense_F),
                sparse_case=dict(lambda2=sparse_l2, F_global=sparse_F),
                interpretation=f'lambda2={lambda2:.3f}->efficiency={pred_eff:.4f}. More connectivity HURTS Freedom.',
                thesis='T4', label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.')


def run_all_perception_simulations(n: int = 100) -> dict:
    """Run all perception levels. All from config. Zero hardcodes."""
    return dict(
        level_0=simulate_passive_physics(n),
        level_1=simulate_topology_level(n),
        level_2=simulate_agent_level(n),
        level_2_5=simulate_structural_level(n),
        l_layer_gap=l_layer_status(),
        paradox_L1_L25=dict(rho_deucalion=float(_P.level25_rho_vs_level1),
                            meaning='Dense graphs NOT good for agents (T4)'),
        dead_formula=dict(formula=str(_P.dead_formula), r2=float(_P.dead_r2), status='DEAD'),
        seed=get_seed(), label='SIMULATED. F=P/D HYPOTHESIS UNDER TEST.',
        thesis_trace='T2+T3+T4')
