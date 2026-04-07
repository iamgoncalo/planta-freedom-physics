"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/result_narrator.py — Convert simulation result → NL explanation.
Max words from cfg.voice.max_response_words. PT or EN. ElevenLabs TTS.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg


def narrate_result(result: dict, language: str = None) -> str:
    """Convert result dict to NL. Respects max_response_words from config."""
    lang     = language or str(cfg.voice.language)
    max_w    = int(cfg.voice.max_response_words)
    F        = result.get("F_composite", result.get("F_global", result.get("F", 0.5)))
    cost     = result.get("cost_eur", result.get("total_eur", 0))
    label    = result.get("label","SIMULATED")
    if lang == "pt":
        text = (f"Resultado: Freedom score F={round(float(F),3)}. "
                f"Custo estimado: €{round(float(cost),0):,.0f}. "
                f"A composição foi optimizada por PSO para maximizar F=P/D. "
                f"Nota: {label}.")
    else:
        text = (f"Result: Freedom score F={round(float(F),3)}. "
                f"Estimated cost: €{round(float(cost),0):,.0f}. "
                f"Composition optimised by PSO to maximise F=P/D. "
                f"Note: {label}.")
    # Truncate to max_response_words
    words = text.split()
    if len(words) > max_w:
        text = " ".join(words[:max_w]) + "..."
    return text
