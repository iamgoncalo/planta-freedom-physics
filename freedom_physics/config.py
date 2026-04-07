"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
config.py — Pydantic-style config loader for Freedom Physics Omega.
Loads config_omega.yaml. Validates ALL weight group sums = 1.0.
Zero hardcoded values. Single source of truth.
"""
from __future__ import annotations
import os, yaml
from types import SimpleNamespace

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config_omega.yaml')
_FALLBACK    = os.path.join(os.path.dirname(__file__), '..', 'config_physics.yaml')

def _load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def _to_namespace(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in d.items()})
    if isinstance(d, list):
        return [_to_namespace(i) for i in d]
    return d

def _load_config() -> SimpleNamespace:
    if os.path.exists(_CONFIG_PATH):
        raw = _load_yaml(_CONFIG_PATH)
    else:
        raw = _load_yaml(_FALLBACK)

    # Assert ALL weight groups sum to 1.0
    _assert_weights(raw.get('atomic_distortion_weights', {}), 'atomic_distortion_weights')
    _assert_weights(raw.get('material_freedom_weights',  {}), 'material_freedom_weights')
    _assert_weights(raw.get('building_distortion_weights',{}), 'building_distortion_weights')
    # salary_segments pct
    segs = raw.get('economics', {}).get('salary_segments', {})
    if segs:
        pct_sum = sum(v.get('pct', 0) for v in segs.values())
        assert abs(pct_sum - 1.0) < 1e-6, \
            f"salary_segments pct sum={pct_sum:.8f} != 1.0"

    return _to_namespace(raw)

def _assert_weights(weights: dict, name: str) -> None:
    if not weights:
        return
    s = sum(weights.values())
    assert abs(s - 1.0) < 1e-6, \
        f"Weight group '{name}' sums to {s:.8f} — must be exactly 1.0"

cfg = _load_config()

def get_seed() -> int:
    return int(cfg.meta.seed)

def get_epsilon() -> float:
    return float(getattr(cfg.economics, 'epsilon', 1e-14))


def get_alpha(context: str = "passive_physics") -> float:
    return float(getattr(cfg.alpha, context, 1.0))

def get_building_weights() -> dict:
    return cfg.building_distortion_weights.__dict__.copy()

def get_atomic_weights() -> dict:
    return cfg.atomic_distortion_weights.__dict__.copy()

def get_material_weights() -> dict:
    return cfg.material_freedom_weights.__dict__.copy()

def get_pso_params() -> dict:
    s = cfg.swarm
    return {
        "n_particles": int(s.pso_particles),
        "n_iterations": int(s.pso_iterations),
        "inertia": float(s.pso_inertia),
        "c1": float(s.pso_c1),
        "c2": float(s.pso_c2),
    }

def get_avoid_rooms() -> list:
    ar = cfg.swarm.avoid_rooms
    return list(ar) if isinstance(ar, list) else [ar]

def get_config() -> SimpleNamespace:
    return cfg

# Verify weight assertions at import
_assert_weights(cfg.atomic_distortion_weights.__dict__, 'atomic_distortion_weights')
_assert_weights(cfg.material_freedom_weights.__dict__,  'material_freedom_weights')
_assert_weights(cfg.building_distortion_weights.__dict__,'building_distortion_weights')

def get_simulated_label() -> str:
    return str(cfg.meta.simulated_label)
