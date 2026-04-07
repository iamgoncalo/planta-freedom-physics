# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
chemistry/periodic_table.py — Freedom-sorted periodic table. 118 elements. T2+T5."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from freedom_physics.elements.periodic_table import (
    PERIODIC_TABLE, BY_Z, freedom_of, most_free, periodic_law_demo)

def freedom_sorted_table(channel="electrical"):
    results=[]
    for sym,el in PERIODIC_TABLE.items():
        F=freedom_of(sym,channel)
        results.append({"Z":el.Z,"symbol":sym,"name":el.name,"period":el.period,
                        "group":el.group,"block":el.block,f"F_{channel}":round(F,4),
                        "thesis":"T2+T5","label":"SIMULATED"})
    return sorted(results,key=lambda x:-x[f"F_{channel}"])

def element_full_profile(symbol):
    el=PERIODIC_TABLE.get(symbol.capitalize())
    if not el: raise KeyError(f"Element {symbol!r} not found.")
    return {"Z":el.Z,"symbol":symbol,"name":el.name,"period":el.period,"group":el.group,
            "F_electrical":round(el.F_electrical(),4),"F_thermal":round(el.F_thermal(),4),
            "F_chemical":round(el.F_chemical(),4),"F_ionize":round(el.F_ionize(),4),
            "F_nuclear":round(el.F_nuclear(),4),"F_structural":round(el.F_structural(),4),
            "thesis":"T2+T5","label":"SIMULATED"}

__all__=["PERIODIC_TABLE","BY_Z","freedom_of","most_free","periodic_law_demo",
         "freedom_sorted_table","element_full_profile"]

def get_freedom_sorted_table(channel: str = "structural") -> list:
    """Return all 118 elements sorted by F_{channel} descending.
    Uses built-in PERIODIC_TABLE only (no mendeleev) for speed.
    """
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE
    ch_map = {
        'structural': lambda el: el.F_structural(),
        'electrical': lambda el: el.F_electrical(),
        'thermal':    lambda el: el.F_thermal(),
        'chemical':   lambda el: el.F_chemical(),
        'nuclear':    lambda el: el.F_nuclear(),
    }
    fn = ch_map.get(channel, lambda el: el.F_structural())
    rows = []
    for sym, el in PERIODIC_TABLE.items():
        val = fn(el)
        rows.append({
            'Z': el.Z, 'symbol': sym,
            f'F_{channel}': round(val, 4),
            'label': 'SIMULATED',
        })
    return sorted(rows, key=lambda e: e[f'F_{channel}'], reverse=True)

def get_group_patterns() -> dict:
    """Return group patterns by Freedom channel."""
    from freedom_physics.elements.periodic_table import PERIODIC_TABLE
    groups = {}
    for sym, el in PERIODIC_TABLE.items():
        g = getattr(el, 'group', 'unknown')
        if g not in groups: groups[g] = []
        groups[g].append(sym)
    return groups
