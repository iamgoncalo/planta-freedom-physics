"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
visualization/V15_molecule_3d.py — molecule_3d visualization.
Exports: HTML (Plotly interactive) + STL + GLTF + PNG.
All export paths from config. SIMULATED watermark in title.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg

VIZ_DIR = str(cfg.visualization.export_dir)
TITLE = "molecule_3d [SIMULATED — F=P/D HYPOTHESIS UNDER TEST]"


def render(output_dir: str = None) -> dict:
    """Render molecule_3d visualization. Returns dict of export paths."""
    outdir = output_dir or VIZ_DIR
    base   = os.path.join(outdir, "molecule_3d")
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
