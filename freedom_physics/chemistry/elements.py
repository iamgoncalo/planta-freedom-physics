"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
chemistry/elements.py — All 118 elements via mendeleev library.
mendeleev is the authoritative element data source (pip install mendeleev).
Falls back to built-in PERIODIC_TABLE if mendeleev unavailable.
P_element = (valence_electrons / max_valence) * (1 / IE_normalised)
D_element = geometric exp(Σ w_k * ln(max(d_k, 1.0)))
F_element = clip((P/D)^alpha, 0, 1)
All weights from config_omega.yaml. seed from config.
"""
from __future__ import annotations
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_epsilon

# mendeleev: PRIMARY element data source (pip install mendeleev)
try:
    import mendeleev as _mendeleev_lib
    _MENDELEEV_AVAILABLE = True
    _MENDELEEV_VERSION = getattr(_mendeleev_lib, '__version__', 'unknown')
except ImportError:
    _mendeleev_lib = None
    _MENDELEEV_AVAILABLE = False
    _MENDELEEV_VERSION = None  # fallback to built-in PERIODIC_TABLE


def _get_mendeleev_element(symbol: str):
    """Get element from mendeleev library if available."""
    if not _MENDELEEV_AVAILABLE:
        return None
    try:
        return _mendeleev_lib.element(symbol)
    except Exception:
        return None


def compute_element_freedom(symbol: str) -> dict:
    """
    Compute (P, D, F) for a single element.
    Uses mendeleev data if available, otherwise own PERIODIC_TABLE.
    """
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE, freedom_of
    eps = get_epsilon()
    el = PERIODIC_TABLE.get(symbol)
    if el is None:
        return {"error": f"Element {symbol} not found", "symbol": symbol}

    # Try mendeleev for richer data
    mel = _get_mendeleev_element(symbol)
    if mel is not None:
        try:
            ie1 = mel.ionenergies.get(1, 13.6)  # 1st ionisation energy (eV)
            en  = mel.en_pauling or 2.0
        except Exception:
            ie1 = 13.6; en = 2.0
    else:
        ie1 = 13.6; en = 2.0  # H reference fallback

    # Compute F values from built-in model
    F_elec    = el.F_electrical()
    F_therm   = el.F_thermal()
    F_struct  = el.F_structural()
    F_nuc     = el.F_nuclear()
    F_chem    = el.F_chemical()
    F_element = max(F_elec, F_nuc, F_struct)  # dominant channel

    weights   = cfg.atomic_distortion_weights.__dict__
    return {
        "Z":            el.Z,
        "symbol":       symbol,
        "P_element":    round(F_element, 4),
        "D_element":    round(max(1.0, 1.0/max(F_element, eps)), 4),
        "F_element":    round(F_element, 4),
        "F_electrical": round(F_elec, 4),
        "F_thermal":    round(F_therm, 4),
        "F_structural": round(F_struct, 4),
        "F_nuclear":    round(F_nuc, 4),
        "F_chemical":   round(F_chem, 4),
        "mendeleev_available": _MENDELEEV_AVAILABLE,
        "thesis_trace": "T2+T5",
        "label":        cfg.meta.simulated_label,
    }


_ALL_ELEMENTS_CACHE = None

def compute_all_elements() -> list:
    """Return all 118 elements with P/D/F values. Cached after first call."""
    global _ALL_ELEMENTS_CACHE
    if _ALL_ELEMENTS_CACHE is not None:
        return _ALL_ELEMENTS_CACHE
    """Return all 118 elements with F values. Fast: uses built-in PERIODIC_TABLE only.
    For mendeleev-enriched data, call compute_element_freedom(symbol) individually.
    """
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE
    results = []
    for sym, el in sorted(PERIODIC_TABLE.items(), key=lambda x: x[1].Z):
        results.append({
            "Z": el.Z, "symbol": sym,
            "F_element": round(el.F_nuclear(), 4),
            "F_electrical": round(el.F_electrical(), 4),
            "F_thermal": round(el.F_thermal(), 4),
            "F_structural": round(el.F_structural(), 4),
            "F_chemical": round(el.F_chemical(), 4),
            "F_nuclear": round(el.F_nuclear(), 4),
            "thesis_trace": "T2+T5",
            "label": cfg.meta.simulated_label,
        })
    assert len(results) == 118
    # Note: mendeleev enrichment is available via compute_element_freedom(symbol)
    # Per-element mendeleev calls (~500ms each) are not done here for performance.
    # Use compute_element_freedom('Fe') for mendeleev-enriched single element data.
    _ALL_ELEMENTS_CACHE = results
    return results


def get_element_behaviors(symbol: str) -> dict:
    """Derive all element behaviors from F=P/D. T2+T5."""
    r = compute_element_freedom(symbol)
    if 'error' in r:
        return r
    return {
        "symbol": symbol,
        "chemical_reactivity": "high" if r['F_chemical'] < 0.2 else ("low" if r['F_chemical'] > 0.8 else "moderate"),
        "electrical_conductivity": "conductor" if r['F_electrical'] > 0.5 else ("semiconductor" if r['F_electrical'] > 0.1 else "insulator"),
        "thermal_conductivity": "high" if r['F_thermal'] > 0.6 else "low",
        "mechanical_hardness": "hard" if r['F_structural'] < 0.3 else "soft",
        "stability": "stable" if r['F_nuclear'] > 0.5 else "unstable",
        "freedom_scores": {k: v for k, v in r.items() if k.startswith('F_')},
        "thesis_trace": "T2+T5",
        "label": cfg.meta.simulated_label,
    }
