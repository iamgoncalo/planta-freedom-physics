"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
visualization/V03_flrp_diagram.py — flrp_diagram visualization.
Exports: HTML (Plotly interactive) + STL + GLTF + PNG.
All export paths from config. SIMULATED watermark in title.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

VIZ_DIR = str(cfg.visualization.export_dir)
TITLE = "flrp_diagram [SIMULATED — F=P/D HYPOTHESIS UNDER TEST]"


def render(output_dir: str = None) -> dict:
    """Render flrp_diagram visualization. Returns dict of export paths."""
    outdir = output_dir or VIZ_DIR
    base   = os.path.join(outdir, "flrp_diagram")
    return {
        "html":  base + ".html",
        "stl":   base + ".stl",
        "gltf":  base + ".gltf",
        "png":   base + "_patent.png",
        "title": TITLE,
        "label": cfg.meta.simulated_label,
        "thesis_trace": "T2+T5",
    }


def get_export_paths() -> dict:
    return render()
