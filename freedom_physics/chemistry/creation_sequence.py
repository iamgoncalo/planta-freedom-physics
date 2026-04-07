"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
chemistry/creation_sequence.py — 12-stage nucleosynthesis as D crystallisation.
T1+T2+T5: creation = progressive D crystallisation from vacuum (D≈0) to synthetic.
Fe (Z=26) = F_nuclear maximum = stellar burning endpoint.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

_STAGES = [
    {"stage": 0,  "name": "Quantum vacuum",          "process": "T1 pure state",
     "D_relative": 0.00, "elements_produced": [],
     "note": "D≈0, maximum Freedom. →=maximum. Big Bang initial condition."},
    {"stage": 1,  "name": "Big Bang — Hydrogen",      "process": "primordial nucleosynthesis",
     "D_relative": 0.10, "elements_produced": [1],
     "note": "H (Z=1): first D crystallisation. 75% of baryonic mass."},
    {"stage": 2,  "name": "Big Bang — Helium",        "process": "primordial nucleosynthesis",
     "D_relative": 0.15, "elements_produced": [2],
     "note": "He (Z=2): first closed shell. 25% of baryonic mass."},
    {"stage": 3,  "name": "Big Bang trace — Li/Be/B", "process": "primordial nucleosynthesis",
     "D_relative": 0.20, "elements_produced": [3,4,5],
     "note": "Lithium gap: extremely low abundance. D begins increasing."},
    {"stage": 4,  "name": "Stellar — CNO cycle",      "process": "hydrogen burning",
     "D_relative": 0.35, "elements_produced": [6,7,8],
     "note": "Carbon (Z=6): triple-alpha process. Life's backbone."},
    {"stage": 5,  "name": "Stellar — Neon/Magnesium", "process": "helium burning",
     "D_relative": 0.45, "elements_produced": [10,12],
     "note": "Shell burning in massive stars. F_nuclear decreasing."},
    {"stage": 6,  "name": "Stellar — Silicon burning", "process": "silicon burning",
     "D_relative": 0.52, "elements_produced": [14,16,18,20],
     "note": "Advanced stellar burning. Si→Fe sequence."},
    {"stage": 7,  "name": "Iron peak — stellar endpoint", "process": "iron-peak nucleosynthesis",
     "D_relative": 0.55, "elements_produced": [24,25,26,27,28],
     "note": "Fe (Z=26): F_nuclear MAXIMUM. ΔF_fusion<0 beyond Fe. Stars stop. T2 Law 2."},
    {"stage": 8,  "name": "s-process — AGB stars",    "process": "slow neutron capture",
     "D_relative": 0.70, "elements_produced": list(range(31,84)),
     "note": "Elements Z=31-82. D increasing. Ga through Pb/Bi."},
    {"stage": 9,  "name": "r-process — neutron stars", "process": "rapid neutron capture",
     "D_relative": 0.82, "elements_produced": list(range(37,93)),
     "note": "Supernovae + neutron star mergers. Heavy elements Z=37-92."},
    {"stage": 10, "name": "Lead — last stable magic", "process": "radioactive decay endpoint",
     "D_relative": 0.85, "elements_produced": [82,83],
     "note": "Pb (Z=82) doubly magic. Bi (Z=83) last stable. Local F_stability max."},
    {"stage": 11, "name": "Thorium/Uranium — r-process", "process": "r-process supernovae",
     "D_relative": 0.92, "elements_produced": [90,92],
     "note": "Very high D_nuclear. Long half-lives. Natural radioactives."},
    {"stage": 12, "name": "Synthetic — artificial",   "process": "artificial D injection",
     "D_relative": 0.98, "elements_produced": list(range(93,119)),
     "note": "Z>92: F≈0. Immediate decay = T2 Law 2 acting. D injection via collider."},
]


def get_all_stages() -> list:
    """Return all 12+ nucleosynthesis stages with AFI D-crystallisation values."""
    return [dict(s, label=cfg.meta.simulated_label, thesis_trace="T1+T2+T5") for s in _STAGES]


def get_stellar_F_nuclear() -> dict:
    """Return {Z: F_nuclear} for elements in stellar burning sequence (Z=1..30)."""
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE
    return {el.Z: el.F_nuclear() for sym, el in PERIODIC_TABLE.items() if el.Z <= 30}


def get_stage_by_element(Z: int) -> dict:
    """Return the creation stage for element with atomic number Z."""
    for s in _STAGES:
        if Z in s["elements_produced"]:
            return s
    return _STAGES[0]  # default: vacuum
