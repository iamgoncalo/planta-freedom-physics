
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"""
from __future__ import annotations
import os, yaml
from pathlib import Path
from types import SimpleNamespace

def _ns(obj):
    if isinstance(obj, dict): return SimpleNamespace(**{k:_ns(v) for k,v in obj.items()})
    if isinstance(obj, list): return [_ns(i) for i in obj]
    return obj

def _load():
    # Look for afi's config_physics.yaml OR lof's config.yaml
    candidates = [
        Path(__file__).parent.parent.parent / "config_physics.yaml",
        Path(__file__).parent.parent.parent / "config.yaml",
        Path(os.getcwd()) / "config_physics.yaml",
        Path(os.getcwd()) / "config.yaml",
    ]
    for p in candidates:
        if p.exists():
            with open(p) as f:
                return _ns(yaml.safe_load(f))
    raise FileNotFoundError("config_physics.yaml or config.yaml not found")

cfg = _load()

def get_building_weights():
    try: w = vars(cfg.building_distortion_weights)
    except AttributeError: w = vars(cfg.building_weights)
    assert abs(sum(w.values())-1.0)<1e-6
    return dict(w)
