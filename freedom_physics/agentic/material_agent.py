"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/material_agent.py — "Build me a house with X, Y, Z" full pipeline.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

def build_from_query(parsed: dict) -> dict:
    from freedom_physics.structures.house_designer import design_house
    result = design_house(parsed.get("elements",["C","Si","Al"]),
                          parsed.get("area_m2", 80.0),
                          parsed.get("budget_eur", 10000.0),
                          parsed.get("priority","structural"))
    return result
