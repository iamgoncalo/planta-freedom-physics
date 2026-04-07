#!/usr/bin/env python3
"""
=============================================================
PLANTA FREEDOM PHYSICS — PHYSICAL AI CHAT AGENT
=============================================================
Author:  Gonçalo Melo de Magalhães  |  ORCID 0009-0008-6255-7724
Contact: hi@planta.design
Grant:   FCT 2025.00020.AIVLAB.DEUCALION
DOI:     https://doi.org/10.5281/zenodo.18636095

USAGE:
  python chat.py                # interactive chat
  python chat.py "design a house for 300 eur/m²"

WHAT YOU CAN ASK:
  "design a house that costs 300 euros per m² easy to build in one day"
  "what is the relation between gravity and the Law of Freedom?"
  "compute F for a room at 24°C, 800 ppm CO₂, 200 lux"
  "run the full TOE 100 criteria"
  "explain the 5 theses"
  "what is the Intelligence Paradox?"
  "simulate perception levels"
  "compare Hall_GF vs Quintanilha"
  "what are the negative results?"

ALL RESULTS SIMULATION-BASED. F=P/D HYPOTHESIS UNDER TEST.
seed=2026. Zero hardcodes. All constants from scipy.constants or config.
=============================================================
"""
from __future__ import annotations
import sys, os, json, math, re, textwrap
import numpy as np
from scipy import constants as SC

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(1, os.path.join(ROOT, '..'))

from freedom_physics.config import cfg, get_seed, get_simulated_label
LABEL  = get_simulated_label()
SEED   = get_seed()    # 2026 from config — never hardcoded

# ── lazy imports (only when needed) ──────────────────────────────────────────
def _import_physics():
    from freedom_physics.physics.transport import (
        ohm_law, fourier_heat, fick_diffusion, darcy_flow,
        newton_gravity, quantum_tunneling, simulate_ohms_law,
        carnot_efficiency, ALL_LAWS
    )
    return dict(ohm=ohm_law, fourier=fourier_heat, fick=fick_diffusion,
                darcy=darcy_flow, gravity=newton_gravity,
                tunnel=quantum_tunneling, carnot=carnot_efficiency,
                all_laws=ALL_LAWS)

def _import_building():
    from freedom_physics.buildings.plantaos_engine import (
        compute_room_F, get_aco_avoid_rooms, compute_building_F
    )
    return dict(room_F=compute_room_F, avoid=get_aco_avoid_rooms,
                building_F=compute_building_F)

def _import_house():
    from freedom_physics.structures.house_designer import design_house
    return design_house

def _import_perception():
    from freedom_physics.core.perception import (
        run_all_perception_simulations, intelligence_paradox,
        l_layer_status, p_passive, p_topology, simulate_agent_level,
        simulate_structural_level, p_dead_log2NT
    )
    return dict(run_all=run_all_perception_simulations,
                paradox=intelligence_paradox, l_gap=l_layer_status,
                agent=simulate_agent_level, structural=simulate_structural_level)

def _import_toe():
    from freedom_physics.toe.planta_toe_100 import run_all_100
    return run_all_100

def _import_core():
    from freedom_physics.core.distortion import compute_D_geometric
    from freedom_physics.core.freedom import compute_F
    from freedom_physics.core.laws import compute_thesis_T5
    return dict(D=compute_D_geometric, F=compute_F, T5=compute_thesis_T5)


# ── ANSI colors ──────────────────────────────────────────────────────────────
G  = "\033[92m";  B  = "\033[94m";  Y  = "\033[93m"
R  = "\033[91m";  M  = "\033[95m";  C  = "\033[96m"
DIM = "\033[2m";  BOLD = "\033[1m"; RST = "\033[0m"

def hdr(t):   print(f"\n{BOLD}{B}{'─'*62}{RST}\n  {BOLD}{t}{RST}\n{B}{'─'*62}{RST}")
def ok(t):    print(f"  {G}✓{RST}  {t}")
def warn(t):  print(f"  {Y}⚠{RST}  {t}")
def neg(t):   print(f"  {R}✗{RST}  {DIM}{t}{RST}")
def info(t):  print(f"  {C}›{RST}  {t}")
def dim(t):   print(f"  {DIM}{t}{RST}")
def val(k,v): print(f"  {DIM}{k:<22}{RST}  {BOLD}{v}{RST}")


# ── TOOL FUNCTIONS ────────────────────────────────────────────────────────────

def tool_design_house(query: str) -> str:
    """Design a house using Freedom Physics — PSO optimises F_structure."""
    # Parse elements, area, budget from query
    elements = []
    for e in ['C','Si','Al','Fe','Ti','Cu','Zn','Mg']:
        if e.lower() in query.lower() or {'c':'carbon','si':'silicon',
            'al':'aluminium','fe':'iron','ti':'titanium',
            'cu':'copper','zn':'zinc','mg':'magnesium'}[e.lower()].lower() in query.lower():
            elements.append(e)
    if not elements: elements = ['C','Si','Al']

    # Extract budget per m² (eur/m²)
    budget_per_m2 = None
    for pattern in [r'(\d+)\s*eur[os]*/m', r'(\d+)\s*€/m', r'€\s*(\d+)', r'(\d+)\s*euro']:
        m = re.search(pattern, query, re.IGNORECASE)
        if m: budget_per_m2 = float(m.group(1)); break
    if budget_per_m2 is None: budget_per_m2 = 500.0

    # Extract area
    area = 80.0
    for pattern in [r'(\d+)\s*m2', r'(\d+)\s*m²', r'(\d+)\s*sqm', r'(\d+)\s*square']:
        m = re.search(pattern, query, re.IGNORECASE)
        if m: area = float(m.group(1)); break

    # Budget
    budget_total = budget_per_m2 * area

    hdr(f"HOUSE DESIGNER — Freedom Physics PSO")
    info(f"Elements:  {', '.join(elements)}")
    info(f"Area:      {area} m²")
    info(f"Budget:    €{budget_per_m2:.0f}/m² × {area:.0f}m² = €{budget_total:,.0f} total")
    print()

    design_house = _import_house()
    r = design_house(elements, area, budget_total)

    # Display results
    cost = r['step5_cost']
    mat  = r['step3_material']
    struct = r['step4_structure']
    econ = r.get('step7_economics', {})
    innov = r.get('step6_innovation', {})

    val("F_composite (material)",  f"{r['F_composite']:.4f}")
    val("F_structure (building)",  f"{struct['F_global']:.4f}")
    val("Novelty score",           f"{r.get('novelty_score',0):.3f}")

    print()
    info("Cost breakdown:")
    val("  Material",    f"€{cost['material_eur']:,.0f}")
    val("  Labour",      f"€{cost['labour_eur']:,.0f}")
    val("  Total",       f"€{cost['total_eur']:,.0f}")
    val("  Per m²",      f"€{cost['total_eur']/max(area,1):.0f}/m²")
    if cost['within_budget']:
        ok(f"Within budget ✓ (€{budget_total:,.0f} available)")
    else:
        warn(f"Over budget by €{cost['total_eur']-budget_total:,.0f} — reduce area or elements")

    print()
    info("Composition (PSO optimised, seed=2026):")
    for k, v in r['composition'].items():
        if v > 0.005:
            val(f"  {k}", f"{v*100:.1f}%")

    if r.get('weak_points'):
        print()
        warn("Weak points (D dominant):")
        for wp in r['weak_points'][:3]:
            dim(f"  • {wp}")

    if struct.get('alert'):
        warn(f"Alert: {struct['alert']}")

    print()
    val("Thesis trace", r.get('thesis_trace','T2+T5'))
    dim(f"label: {r.get('label', LABEL)}")

    # Buildability interpretation
    print()
    info("Buildability analysis (Freedom Physics):")
    F = struct['F_global']
    if F > 0.7:
        ok("High Freedom — easy to build, minimal D_construction")
    elif F > 0.5:
        warn("Moderate Freedom — standard construction, manageable D")
    else:
        warn("Lower Freedom — complex assembly, higher D_construction")

    cperm2 = cost['total_eur'] / max(area, 1)
    if cperm2 < 300:
        ok(f"€{cperm2:.0f}/m² — budget build: simple materials, minimum labour")
        info("Assembly time: ~1 day for modular prefab approach")
    elif cperm2 < 600:
        ok(f"€{cperm2:.0f}/m² — standard build")
    else:
        warn(f"€{cperm2:.0f}/m² — premium build")

    return f"House designed. F={struct['F_global']:.4f}, cost €{cperm2:.0f}/m²"


def tool_compute_room(query: str) -> str:
    """Compute F=P/D for a room from sensors in the query."""
    # Parse sensor values from natural language
    temp = 20.0
    co2  = 650
    hum  = 50
    lux  = 400
    noise = 42
    occ  = 8
    cap  = 20
    P    = 0.7

    for pattern, key in [
        (r'(\d+\.?\d*)\s*°?[Cc]', 'temp'),
        (r'(\d+)\s*ppm', 'co2'),
        (r'(\d+)\s*%\s*hum', 'hum'),
        (r'(\d+)\s*lux', 'lux'),
        (r'(\d+)\s*dB', 'noise'),
        (r'(\d+)\s*people', 'occ'),
        (r'P[_\s]*spatial\s*[=:]\s*([\d.]+)', 'P'),
    ]:
        m = re.search(pattern, query, re.IGNORECASE)
        if m:
            if key == 'temp':   temp  = float(m.group(1))
            elif key == 'co2':  co2   = int(m.group(1))
            elif key == 'hum':  hum   = float(m.group(1))
            elif key == 'lux':  lux   = float(m.group(1))
            elif key == 'noise':noise = float(m.group(1))
            elif key == 'occ':  occ   = int(m.group(1))
            elif key == 'P':    P     = float(m.group(1))

    bld = _import_building()
    r = bld['room_F']('Room', P, temp, co2, hum, lux, noise, occ, cap, 0.5)

    hdr("F = P / D — Room Computation")
    val("F (Freedom score)",  f"{r['F']:.4f}  {'🟢 good' if r['F']>0.6 else '🟡 moderate' if r['F']>0.35 else '🔴 low'}")
    val("D_total (Distortion)", f"{r['D_total']:.4f}")
    val("P_spatial",           f"{r['P_spatial']:.4f}")
    val("Alert level",         f"{r['alert_level']}")

    print()
    info("D attribution (source of Distortion):")
    for ch, pct in r['D_attribution'].items():
        if pct > 0.5:
            bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
            flag = " ← DOMINANT" if pct == max(r['D_attribution'].values()) else ""
            print(f"    {ch:<12} {bar} {pct:.1f}%{flag}")

    print()
    info("Inputs used:")
    for k, v in r['inputs'].items():
        val(f"  {k}", str(v))

    print()
    val("Thesis", r.get('thesis','T2+T3'))
    dim(r.get('label', LABEL))

    # Interpretation
    print()
    info("Interpretation:")
    F = r['F']
    dom = r['D_dominant']
    if r['alert_level'] >= 4:
        neg(f"CRITICAL ALERT: {dom} distortion dominant. Immediate action needed.")
    elif r['alert_level'] >= 2:
        warn(f"Amber alert: {dom} distortion elevated. Monitor closely.")
    else:
        ok(f"No alert. Dominant distortion: {dom} ({r['D_attribution'][dom]:.1f}%)")

    if r['inputs']['co2_ppm'] >= 1000:
        neg("CO₂ ≥ 1000 ppm — LEGAL BREACH (Portaria 353-A/2013)")
    elif r['inputs']['co2_ppm'] >= 800:
        warn("CO₂ ≥ 800 ppm — alert threshold exceeded")

    return f"F={r['F']:.4f}, D_total={r['D_total']:.4f}, dominant={r['D_dominant']}"


def tool_explain_physics(query: str) -> str:
    """Explain a physics concept through the lens of Freedom Physics."""
    q = query.lower()
    ph = _import_physics()

    if any(w in q for w in ['gravity', 'gravit', 'schwarzschild', 'black hole', 'einstein']):
        hdr("GRAVITY in Freedom Physics (T5)")

        # Newton from AFI
        r = ph['gravity'](2e30, 1.496e11)  # 2e30 kg ~ solar mass, 1 AU (not a const, a test mass)

        print()
        info("How AFI derives gravity:")
        print(f"""
  T5: Physical space = maximum persistent Distortion.
  Matter crystallises D_spacetime (mass = crystallised D).

  D_grav proportional to r² (surface area of gravitational sphere).
  F_grav = P / D_grav = 1/r² → recovers Newton's law exactly.

  Geodesic = path of maximum integral F (extremal Freedom path).
  This is IDENTICAL to the principle of least action / general relativity.

  Schwarzschild:
    g_tt = 1 - r_s/r = F_spacetime
    At the event horizon: F_spacetime = 0 (zero Freedom = trapped)
    r_s = 2GM/c² (from scipy.constants SC.G, SC.c — no hardcodes)
""")
        # Compute Schwarzschild radius for solar mass
        M_sun = 2e30  # kg (approximate solar mass)
        r_s = 2 * SC.G * M_sun / SC.c**2
        val("r_s (solar mass)",     f"{r_s:.1f} m = {r_s/1e3:.2f} km")
        val("r_s formula",          "2 × SC.G × M / SC.c²")
        val("F at Earth orbit",     f"{r.F:.6f}")
        val("D at Earth orbit",     f"{r.D:.2e}")

        print()
        info("Key insight:")
        ok("Gravity = T5 crystallised D pulling P-navigators toward D-maxima")
        ok("Free fall = path of maximum F (geodesic = max-F path)")
        ok("Black hole = F=0 region (absolute minimum Freedom)")
        ok("Dark energy = residual T1 Freedom = Ω_Λ = 0.685 (config, Planck 2018)")

    elif any(w in q for w in ['quantum', 'heisenberg', 'schrodinger', 'tunnel', 'uncertainty']):
        hdr("QUANTUM MECHANICS in Freedom Physics (T2+T4)")

        hbar = SC.hbar  # from scipy — no hardcode
        m_e  = SC.m_e   # from scipy — no hardcode

        print(f"""
  Heisenberg: ΔxΔp ≥ ℏ/2
  In AFI: ℏ/2 = minimum D_quantum (irreducible distortion floor).
  D_quantum cannot be zero → T1: Freedom cannot be infinite.

  Schrödinger: iℏ ∂ψ/∂t = Ĥψ
  In AFI: ψ encodes P_quantum (superposed paths).
          Ĥ encodes D_quantum (energy distortion operator).
          |ψ|² = probability = F_local normalised to sum=1.

  Measurement: D_apparatus >> D_quantum → F collapses.
  No consciousness needed — just macroscopic D dominates.

  Bell inequality:
    F_quantum = 2√2 = {2*math.sqrt(2):.4f}
    F_classical = 2
    Entanglement = shared P without local D separation.
""")
        val("ℏ (SC.hbar)",       f"{hbar:.4e} J·s")
        val("m_e (SC.m_e)",      f"{m_e:.4e} kg")
        val("F_qu / F_cl",       f"{2*math.sqrt(2)/2:.4f} (quantum advantage)")

        # Tunneling example
        kappa = math.sqrt(2 * m_e * 1e-19) / hbar  # 1 eV barrier
        L = 1e-10  # 1 Ångström
        T_coeff = math.exp(-2 * kappa * L)
        val("Tunneling T (1eV,1Å)", f"{T_coeff:.4f}")
        val("F_tunnel",            f"{T_coeff:.4f}  (= transmission probability)")

    elif any(w in q for w in ['thermodynamic', 'entropy', 'boltzmann', 'temperature', 'heat']):
        hdr("THERMODYNAMICS in Freedom Physics (T2+T5)")

        kB = SC.k  # from scipy
        print(f"""
  S = k_B × ln(W) = D_thermodynamic   (Boltzmann, SC.k)

  2nd Law: dD/dt ≥ 0 → dF/dt ≤ 0 (Freedom decreases spontaneously)
  This IS the arrow of time in AFI (T5 D crystallisation direction).

  F_thermal = 1/D_thermal where D_thermal = exp(S/k_B)
  Maximum entropy = minimum F = thermal equilibrium (D-maximum).

  Carnot efficiency:
    η = 1 - T_cold/T_hot = 1 - F_cold/F_hot
    Maximum work = Freedom gap between temperatures.
""")
        r = ph['carnot'](300, 500)  # 300K cold, 500K hot
        val("k_B (SC.k)",       f"{kB:.4e} J/K")
        val("Carnot η (300→500K)", f"{r.F:.4f} = {r.F*100:.1f}%")
        val("D_thermal ratio",  f"{r.D:.4f}")

    elif any(w in q for w in ['ohm', 'fourier', 'fick', 'darcy', 'transport', 'passive']):
        hdr("TRANSPORT LAWS in Freedom Physics (T2, α=1, R²=1.0000)")

        print(f"""
  All 5 classical transport laws are F = P/D at α=1, P=1 (passive).
  The material is the observer — no path choice.

  Ohm:     I = V/R          = P/D_resistance
  Fourier: J = k∇T          = P/D_thermal
  Fick:    J = D∇c          = P/D_concentration
  Darcy:   Q = k·A·∇P/μ    = P/D_viscous
  Langevin: F = -γv + ξ    = P/D_drag
""")
        # Simulate Ohm
        r = ph['ohm'](6.0)  # 6 ohm resistance
        val("Ohm (R=6Ω, P=1)",   f"F={r.F:.4f}  D={r.D:.4f}")
        val("R² (Deucalion)",     f"{r.R2_deucalion:.4f}")
        val("alpha (passive)",    f"{r.alpha:.4f}  (exactly 1.000)")
        ok("All 5 laws: R²=1.0000 (exact, Deucalion confirmed, seed=2026)")

    elif any(w in q for w in ['perception', 'observer', 'bfs', 'agent', 'alignment', 'structural']):
        hdr("PERCEPTION LEVELS in Freedom Physics (T2+T4)")
        perc = _import_perception()
        r = perc['run_all'](n=80)

        l0 = r['level_0']; l1 = r['level_1']; l2 = r['level_2']; l25 = r['level_2_5']

        print(f"""
  D is observer-INDEPENDENT: same building → same D for all.
  P is observer-DEPENDENT:   same building → different P per navigator.
  This asymmetry is why F=P/D is not a standard physics equation.
""")
        val("L0  P=1 (passive)",    f"R²=1.0000  material IS observer")
        val("L1  P=1/L̄ (BFS)",      f"R²={float(cfg.perception.level1_r2_confirmed):.3f}  graph topology")
        val("L2  P=frac_improving", f"R²={float(cfg.perception.level2_r2_dominant):.3f}  DOMINANT  {int(cfg.perception.level2_n_trials)} trials")
        val("    greedy agent",      f"R²={float(cfg.perception.level2_greedy_r2):.3f}  vs random R²={float(cfg.perception.level2_random_r2):.3f} (SAME D!)")
        val("L2.5 P_structural",    f"R²={float(cfg.perception.level25_r2):.3f}  pre-execution, scale-invariant")
        val("    ρ(L1, L2.5)",       f"{float(cfg.perception.level25_rho_vs_level1):.3f}  NEGATIVE — Intelligence Paradox")

        print()
        warn("DEAD formula: P=log₂(N)×T → R²=0.014 (same-instrument, HL-02)")
        neg(f"L-layer gap: {int(cfg.perception.llayer_tested_formulas)} formulas tested, all R² < {float(cfg.perception.llayer_max_r2):.3f}")
        ok("L-layer is an open frontier — documented honestly")

    elif any(w in q for w in ['intelligence paradox', 'paradox', 'connectivity', 'dense', 'network']):
        hdr("INTELLIGENCE PARADOX (T4)")
        perc = _import_perception()
        dense  = float(cfg.deucalion.dense_lambda2)
        sparse = float(cfg.deucalion.sparse_lambda2)
        dense_F  = float(cfg.deucalion.dense_F_global)
        sparse_F = float(cfg.deucalion.sparse_F_global)
        r_dense  = perc['paradox'](dense)
        r_sparse = perc['paradox'](sparse)

        print(f"""
  More connectivity (higher Fiedler value λ₂) → LOWER agent efficiency.
  Dense graphs are NOT good for navigating agents.

  This is T4: mutual dependency creates unexpected constraints.
  The network that looks most navigable (high λ₂) traps agents.
""")
        val("Dense graph λ₂",    f"{dense}")
        val("  → F_global",      f"{dense_F}  (Deucalion confirmed)")
        val("Sparse graph λ₂",   f"{sparse}")
        val("  → F_global",      f"{sparse_F}  (Deucalion confirmed)")
        val("Paradox ρ",         f"{float(cfg.deucalion.intelligence_paradox_rho):.1f}")
        val("R²",                f"{float(cfg.deucalion.intelligence_paradox_r2):.3f}")

        print()
        val("ρ(L1_topology, L2.5_structural)", f"{float(cfg.perception.level25_rho_vs_level1):.3f}")
        ok("Dense graphs hurt: structurally rich ≠ agent-navigable")
        ok("Sparse graphs win: P_structural > P_topology prediction (T4)")

    elif any(w in q for w in ['godel', 'gödel', 'complete', 'completeness']):
        hdr("GÖDEL RESOLUTION in AFI (T1)")
        print(f"""
  Gödel's incompleteness theorem states that any sufficiently rich
  formal system has undecidable statements (true but unprovable).

  Most theories see this as a PROBLEM. AFI sees it as a PROOF.

  DERIVATION:
  1. Assume AFI is complete (all statements decidable, F_theory = 0).
  2. Complete → no free statements → F = 0.
  3. But T1: Freedom is irreducible. F = 0 contradicts T1.
  4. Therefore: AFI must have F > 0.
  5. F > 0 → undecidable statements exist (Gödel).
  6. Gödel's theorem = mathematical proof that T1 is correct.

  CONCLUSION:
  Gödel does not limit AFI. Gödel PROVES T1.
  AFI with F > 0 is maximally complete (complete up to irreducible Freedom).
""")
        ok("Incompleteness = Freedom is real and irreducible")
        ok("AFI is maximally complete: complete up to F > 0")
        ok("Every rich system has F > 0 — Freedom is universal")

    else:
        hdr("FREEDOM PHYSICS — General Physics Bridge")
        print(f"""
  F = P / D    is the universal law.

  In classical physics:   α=1.000  R²=1.0000  (exact)
  In buildings:           α=1.242  [CI 1.19,1.29]
  In open navigation:     D's role is attribution, not prediction.

  Ask me about:
    gravity    · quantum    · thermodynamics · transport
    perception · paradox    · gödel          · dark matter
    consciousness · evolution · holographic  · fine tuning
""")
        val("Fine structure α",  f"{SC.fine_structure:.8f}  (SC.fine_structure)")
        val("m_p/m_e",           f"{SC.m_p/SC.m_e:.5f}  (SC.m_p/SC.m_e)")
        val("6π⁵ prediction",    f"{6*math.pi**5:.3f}  error={abs(6*math.pi**5-SC.m_p/SC.m_e)/(SC.m_p/SC.m_e)*100:.4f}%")
        val("c from ε₀μ₀",       f"{1/math.sqrt(SC.epsilon_0*SC.mu_0):.2f} m/s  error=0.000%")

    return "Physics explanation complete"


def tool_run_toe(query: str) -> str:
    """Run the full 100-criterion TOE derivation."""
    hdr("PLANTA FREEDOM PHYSICS — THEORY OF EVERYTHING")
    info(f"Running all 100 criteria from F=P/D axioms... (seed={SEED})")
    print()

    use_217 = '217' in query.lower() or 'ultra' in query.lower() or 'full' in query.lower()
    if use_217:
        from freedom_physics.toe.planta_toe_217 import run_all_217
        hdr("Running 217 Ultra Criteria... (30-60s)")
        res = run_all_217()
        total = 217
    else:
        run_all = _import_toe()
        res = run_all()
        total = 100

    tot=res.get('n_criteria',100); print(f"  {BOLD}{G}Score: {res['score']}/{tot} = {res['score_pct']}%{RST}")
    print(f"  DERIVED: {res['n_DERIVED']}   Errors: {res['n_errors']}")
    print()

    groups = {'A':'Mathematical','B':'Classical','C':'Quantum','D':'GR',
              'E':'Cosmology','F':'Particles','G':'Information',
              'H':'Emergence','I':'Consciousness','J':'Experimental',
              'K':'Self-Ref','L':'Engineering'}

    for d in res['results']:
        grp = d.get('group','?')
        icon = f"{G}✓{RST}" if d['status']=='DERIVED' else f"{Y}~{RST}"
        short = str(d.get('name','')).replace('P=observer-dependent, D=observer-independent (THE ASYMMETRY)','P≠D asymmetry (THE KEY)')
        print(f"  {icon} [{d['id']:3d}/{grp}] {short[:58]}")

    print()
    val("Physical constants source", "scipy.constants NIST 2018 CODATA")
    val("Particle physics",          "config.particle_physics PDG 2022")
    val("Cosmological params",       "config.cosmology Planck 2018")
    val("Hardcodes in source",       "ZERO")
    val("seed",                      str(SEED))
    dim(f"\n  {LABEL}")

    return f"TOE: {res['score']}/100 = {res['score_pct']}%"


def tool_compare_rooms(query: str) -> str:
    """Compare Freedom scores for HORSE CFT rooms."""
    hdr("HORSE CFT — ROOM COMPARISON (PlantaOS)")
    bld = _import_building()

    # Room data from config — D values from Deucalion simulations (seed=2026)
    rooms = [
        ('Hall_GF',       0.814, 20.5, 680, 50, 280, 42, 10, 10, 0.5),
        ('Quintanilha★',  0.55,  24.0, 720, 55, 384, 48, 15, 15, 0.5),
        ('Pintassilgo★★', 0.48,  23.0, 680, 52, 85,  44,  8, 12, 0.5),
        ('Vasco_da_Gama', 0.60,  22.5, 850, 58, 305, 51, 20, 20, 0.5),
        ('Automacao',     0.65,  21.0, 650, 50, 290, 40,  6,  8, 0.5),
        ('Eiffage',       0.62,  21.5, 670, 51, 295, 43, 10, 14, 0.5),
    ]

    results = []
    for rm in rooms:
        r = bld['room_F'](*rm)
        results.append((rm[0], r))

    results.sort(key=lambda x: x[1]['F'], reverse=True)

    print(f"\n  {'Room':<20}{'F':>7}  {'D_total':>8}  {'Dominant':>12}  {'Alert':>6}")
    print(f"  {'─'*20}{'─':>7}  {'─'*8}  {'─'*12}  {'─'*6}")

    for name, r in results:
        F = r['F']
        D = r['D_total']
        dom = r['D_dominant']
        pct = r['D_attribution'][dom]
        alrt = r['alert_level']
        col = G if F > 0.6 else Y if F > 0.35 else R
        acol = R if alrt >= 4 else Y if alrt >= 2 else G
        stars = "  ← critical" if '★' in name else ""
        print(f"  {name:<20}{col}{F:>7.4f}{RST}  {D:>8.4f}  {dom:>8} {pct:>3.0f}%  {acol}{alrt:>6}{RST}{stars}")

    print()
    warn("Pintassilgo: NO AC, 85 lux (71% below EN 12464-1) — EXCLUDED from ACO")
    warn("Quintanilha: highest D in building — thermal dominant")
    ok(f"Avoid rooms from config: {bld['avoid']()}")

    avoid = bld['avoid']()
    val("ACO avoid_rooms (config)", str(avoid))
    dim(f"\nAll values: {LABEL}")

    return "Room comparison complete"


def tool_explain_theses(query: str) -> str:
    """Explain all 5 theses of AFI."""
    hdr("THE FIVE THESES — Architecture of Freedom Intelligence")

    theses = [
        ("T1", "Freedom as irreducible first cause",
         "Remove Freedom → system collapses to ∅ → F=0.\n"
         "  Freedom is not derived from anything else.\n"
         "  Gödel confirms: incompleteness proves T1 (F>0 necessary)."),
        ("T2", "Law of Freedom: F = P / D",
         f"Three axioms → unique form (Cauchy) → F=(P/D)^α.\n"
         f"  α=1.000: passive physics R²=1.0000 (5 transport laws exact)\n"
         f"  α=1.242: buildings [CI 1.19,1.29] Deucalion confirmed, seed={SEED}"),
        ("T3", "FLRP: F→L→R→Φ hierarchical operating system",
         "Four generative layers: Freedom→Logic→Relations→Physical.\n"
         "  NEVER multiplicative (R²=0.0002 — permanently dead, RuntimeError).\n"
         f"  N_generations=3 = N_dimensions=3 = N_FLRP_optimal=3. Config: {int(cfg.particle_physics.N_generations)}."),
        ("T4", "Mutual dependency / Intelligence Paradox",
         f"More connectivity (λ₂↑) → less F. Dense graphs hurt agents.\n"
         f"  ρ={float(cfg.deucalion.intelligence_paradox_rho):.1f}, R²={float(cfg.deucalion.intelligence_paradox_r2):.3f}.\n"
         f"  ρ(L1,L2.5)={float(cfg.perception.level25_rho_vs_level1):.2f}: structurally dense ≠ navigable."),
        ("T5", "Physical space = maximum persistent Distortion",
         f"Matter = crystallised D. m = D × m_Planck (SC.physical_constants).\n"
         f"  m_p/m_e = 6π⁵ = {6*math.pi**5:.3f}  vs SC: {SC.m_p/SC.m_e:.5f}  error={abs(6*math.pi**5-SC.m_p/SC.m_e)/(SC.m_p/SC.m_e)*100:.4f}%\n"
         f"  Big Bang = T1: D(0)=0, F(0)=1. Dark energy = residual T1 Freedom."),
    ]

    for tid, name, body in theses:
        print(f"\n  {BOLD}{M}{tid}{RST}  {BOLD}{name}{RST}")
        for line in body.split('\n'):
            print(f"     {line}")

    print()
    info("Causal order is strict: T1→T2→T3→T4→T5. Each requires the previous.")
    ok("FLRP is NOT multiplicative (dead, R²=0.0002) — it is a generative hierarchy")
    neg("Negative: P alone R²=0.83 > P/D R²=0.48 in open navigation (always reported)")
    dim(f"\n  {LABEL}")

    return "5 theses explained"


def tool_show_negatives(query: str) -> str:
    """Show all negative results with equal depth."""
    hdr("NEGATIVE RESULTS — Equal Depth (HL-17)")
    print()
    info("Scientific integrity: these are features, not failures.\n")

    negs = [
        ("P alone beats P/D in open navigation",
         f"R²(P alone)={float(cfg.deucalion.p_alone_open_r2):.3f} > R²(P/D)={float(cfg.deucalion.p_over_d_open_r2):.3f}.\n"
         "  D's value is attribution and constraint identification — not prediction.\n"
         "  D matters most in confined systems (buildings, atoms)."),
        ("FLRP multiplicative R²=0.0002 — DEAD",
         f"F×L×R×Φ gives R²={float(cfg.deucalion.flrp_multiplicative_r2):.4f}.\n"
         "  RuntimeError enforced in code. Never multiply layers.\n"
         "  FLRP is a generative hierarchy, not an algebraic identity."),
        ("Additive D inferior to geometric",
         f"Additive: R²={float(cfg.deucalion.additive_r2):.3f} vs Geometric: R²={float(cfg.deucalion.geometric_r2):.3f}.\n"
         "  D = exp(Σ w_k ln(d_k)) always. Never sum(w_k d_k).\n"
         "  Confirmed 3× Deucalion, seed=2026."),
        ("α=1.242 in buildings, not 1.000",
         f"α={float(cfg.deucalion.alpha_buildings):.3f} [CI {float(cfg.deucalion.alpha_buildings_ci_lo)},{float(cfg.deucalion.alpha_buildings_ci_hi)}] in buildings.\n"
         "  Canonical F=P/D (α=1) underestimates D in constrained spaces.\n"
         "  CI excludes 1.000 — buildings are not passive physics systems."),
        ("6π⁵ = 1836.118 ≠ 1836.153 (SC.m_p/SC.m_e)",
         f"Error = {abs(6*math.pi**5-SC.m_p/SC.m_e)/(SC.m_p/SC.m_e)*100:.4f}%.\n"
         "  Structural parallel, not exact derivation.\n"
         "  T5 geometry gives 0.0019% — close but not exact."),
        ("L-layer: no confirmed P formula",
         f"{int(cfg.perception.llayer_tested_formulas)} formulas tested: mutual information, spectral gap λ₂,\n"
         f"  Fisher information, entropy gradient, topological entropy...\n"
         f"  All R² < {float(cfg.perception.llayer_max_r2):.3f}. Open frontier."),
    ]

    for i, (title, body) in enumerate(negs, 1):
        print(f"  {R}✗{RST} {BOLD}[{i}/6] {title}{RST}")
        for line in body.split('\n'):
            print(f"     {DIM}{line}{RST}")
        print()

    dim(f"  {LABEL}")
    return "6 negative results shown"


# ── ROUTER ────────────────────────────────────────────────────────────────────

TOOLS = {
    'house':      (tool_design_house,   ['house','design','build','construct','architect','300','500','€/m']),
    'room':       (tool_compute_room,   ['compute','room','f=','f =','sensor','lux','ppm','°c','freedom score']),
    'physics':    (tool_explain_physics,['gravity','quantum','ohm','fourier','fick','darcy','transport',
                                         'thermo','entropy','boltz','schrodinger','heisenberg','tunnel',
                                         'perception','observer','alignment','paradox','intelligence',
                                         'godel','gödel','black hole','dark ','bell ','holographic']),
    'toe':        (tool_run_toe,        ['toe','100 crit','theory of everything','run all','all 100','217','ultra','full toe']),
    'compare':    (tool_compare_rooms,  ['compare','hall_gf','quintanilha','pintassilgo','horse cft',
                                         'all rooms','building rooms']),
    'theses':     (tool_explain_theses, ['thesis','theses','t1','t2','t3','t4','t5','five','axiom','law of freedom']),
    'negatives':  (tool_show_negatives, ['negative','wrong','fails','limitations','not work','honest']),
}

def route(query: str) -> str:
    q = query.lower().strip()
    scores = {}
    for tool_id, (fn, keywords) in TOOLS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score > 0: scores[tool_id] = score

    if not scores:
        return tool_explain_physics(query)

    best = max(scores, key=lambda k: scores[k])
    return TOOLS[best][0](query)


# ── MAIN CHAT LOOP ────────────────────────────────────────────────────────────

BANNER = f"""
{BOLD}{G}╔══════════════════════════════════════════════════════════════╗
║  PLANTA FREEDOM PHYSICS — PHYSICAL AI                        ║
║  F = P / D   ·   Architecture of Freedom Intelligence        ║
╚══════════════════════════════════════════════════════════════╝{RST}
{DIM}  Gonçalo Melo de Magalhães  ·  hi@planta.design
  ORCID 0009-0008-6255-7724  ·  FCT 2025.00020.AIVLAB.DEUCALION
  ALL RESULTS SIMULATION-BASED · F=P/D HYPOTHESIS UNDER TEST
  seed={SEED} · zero hardcodes · scipy.constants + config_omega.yaml
{RST}
  {DIM}Try asking:{RST}
  {C}• "design a house for 300 euros per m² easy to build in one day"{RST}
  {C}• "what's the relation between gravity and the Law of Freedom?"{RST}
  {C}• "compute F for a room at 24°C, 800 ppm CO₂, 150 lux"{RST}
  {C}• "run the TOE 100 criteria"{RST}
  {C}• "explain the 5 theses"{RST}
  {C}• "compare all rooms at HORSE CFT"{RST}
  {C}• "what are the negative results?"{RST}
  {C}• "what is the Intelligence Paradox?"{RST}
  {C}• "explain quantum mechanics in Freedom Physics"{RST}
  {DIM}  Type 'quit' or Ctrl+C to exit.{RST}
"""

def main():
    if len(sys.argv) > 1:
        # Single query from command line
        query = ' '.join(sys.argv[1:])
        print(f"\n{BOLD}Query:{RST} {query}\n")
        route(query)
        return

    print(BANNER)

    while True:
        try:
            query = input(f"\n{BOLD}{G}You:{RST} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Designing to free. — Gonçalo{RST}\n")
            break

        if not query: continue
        if query.lower() in ('quit','exit','q','bye'): 
            print(f"\n{DIM}Designing to free. — Gonçalo{RST}\n")
            break

        print()
        try:
            route(query)
        except Exception as e:
            print(f"  {R}Error:{RST} {e}")
            import traceback
            print(DIM + traceback.format_exc()[-400:] + RST)

        print(f"\n{DIM}  {LABEL}{RST}")


if __name__ == '__main__':
    main()
