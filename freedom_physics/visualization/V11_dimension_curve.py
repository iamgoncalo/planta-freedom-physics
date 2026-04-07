"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
visualization/V11_dimension_curve.py — dimension_curve visualization.
Exports: HTML (Plotly interactive) + STL + GLTF + PNG.
All export paths from config. SIMULATED watermark in title.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

VIZ_DIR = str(cfg.visualization.export_dir)
TITLE = "dimension_curve [SIMULATED — F=P/D HYPOTHESIS UNDER TEST]"


def render(output_dir: str = None) -> dict:
    """Render dimension_curve visualization. Returns dict of export paths."""
    outdir = output_dir or VIZ_DIR
    base   = os.path.join(outdir, "dimension_curve")
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
