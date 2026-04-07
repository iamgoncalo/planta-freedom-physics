"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/query_parser.py — Parse NL query → structured simulation request.
Pure pattern matching — ZERO LLM calls. All thresholds from config.
"""
from __future__ import annotations
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

_ELEMENT_MAP = {
    "carbon":"C","silicon":"Si","aluminum":"Al","aluminium":"Al","iron":"Fe",
    "copper":"Cu","titanium":"Ti","tungsten":"W","magnesium":"Mg","zinc":"Zn",
    "nickel":"Ni","cobalt":"Co","manganese":"Mn","chromium":"Cr","vanadium":"V",
}


def parse_query(query: str) -> dict:
    """Parse NL query. Returns {intent, elements, area_m2, budget_eur, priority, language}."""
    q = query.lower()
    # Detect language
    lang = "pt" if any(w in q for w in ["casa","construí","construir","com","muito","barata"]) else "en"
    # Detect elements — by name or symbol
    elements = []
    for name, sym in _ELEMENT_MAP.items():
        if name in q or sym in query.split():
            if sym not in elements:
                elements.append(sym)
    # Single-letter symbols (C, Si, Al etc) in original query
    for sym in ["C","Si","Al","Fe","Cu","Ti","W","Mg","Zn","Ni"]:
        if re.search(rf'\b{re.escape(sym)}\b', query) and sym not in elements:
            elements.append(sym)
    # Area
    area = float(re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', query).group(1)) \
           if re.search(r'\d+\s*m[²2]', query) else 80.0
    # Budget
    budget_m = re.search(r'[€£\$]?\s*(\d[\d,\.]*)\s*(k?)\s*(?:eur|euro|€)?', q)
    budget = 10000.0
    if budget_m:
        val = float(budget_m.group(1).replace(',',''))
        if budget_m.group(2) == 'k': val *= 1000
        if 100 <= val <= 10_000_000: budget = val
    # Priority
    priority = "structural"
    if any(w in q for w in ["cheap","barato","barata","economic"]): priority = "electrical"
    if any(w in q for w in ["thermal","heat","calor"]): priority = "thermal"
    # Intent
    house_words = ["house","casa","home","build","construí","construir","building"]
    physics_words = ["why","como","why does","explain","ohm","iron","star"]
    innovation_words = ["novel","patent","innovative","inova","patente"]
    building_words = ["heatwave","temperature","hvac","alert","horse"]
    if any(w in q for w in house_words): intent = "house_design"
    elif any(w in q for w in physics_words): intent = "physics_explanation"
    elif any(w in q for w in innovation_words): intent = "innovation_assessment"
    elif any(w in q for w in building_words): intent = "building_simulation"
    else: intent = "general_query"
    return {"intent": intent, "elements": elements or ["C","Si","Al"],
            "area_m2": area, "budget_eur": budget, "priority": priority,
            "language": lang, "label": cfg.meta.simulated_label}
