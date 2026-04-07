"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/freedom_agent.py — Main router agent. NL → correct sub-agent.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg
from freedom_physics.agentic.query_parser import parse_query
from freedom_physics.agentic.result_narrator import narrate_result

def ask(query: str) -> dict:
    parsed = parse_query(query)
    intent = parsed["intent"]
    if intent == "house_design":
        from freedom_physics.agentic.material_agent import build_from_query
        return build_from_query(parsed)
    elif intent == "physics_explanation":
        from freedom_physics.agentic.physics_agent import explain_physics
        return explain_physics(query)
    elif intent == "building_simulation":
        from freedom_physics.agentic.building_agent import simulate_scenario
        return simulate_scenario()
    elif intent == "innovation_assessment":
        from freedom_physics.agentic.innovation_agent import assess_novelty
        comp = {e: 1/len(parsed["elements"]) for e in parsed["elements"]}
        return assess_novelty(comp, query)
    return {"intent": intent, "parsed": parsed, "label": cfg.meta.simulated_label}
