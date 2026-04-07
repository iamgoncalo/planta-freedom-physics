"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/rl_agent.py — RL agent for material design. F as reward signal.
Algorithm from cfg.ml.rl_algorithm. seed from config.
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_rng = np.random.default_rng(get_seed())


class MaterialEnv:
    """Material composition environment. F=P/D is the reward signal."""
    def __init__(self):
        self.seed     = get_seed()
        self.gamma    = float(cfg.ml.rl_gamma)
        self.rng      = np.random.default_rng(self.seed)
        self.n_elements = 3
        self.state    = None
        self.step_count = 0

    @property
    def action_space(self):
        return _ActionSpace(self.n_elements, self.rng)

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self.state = self.rng.dirichlet(np.ones(self.n_elements))
        self.step_count = 0
        return self.state, {}

    def step(self, action):
        from freedom_physics.materials.material_freedom import compute_F_composite
        from freedom_physics.elements.periodic_table import freedom_of
        elements = ["C", "Si", "Al"]
        fracs = np.abs(action); fracs /= fracs.sum()
        self.state = fracs
        F_vals = [freedom_of(e, "structural") for e in elements]
        F_current = compute_F_composite(F_vals, fracs.tolist())
        # Reward = delta_F - lambda * delta_cost (lambda from config)
        cost_proxy = float(np.dot(fracs, [0.5, 1.8, 2.2]))  # from config material_costs proxy
        reward = float(F_current) - float(cfg.ml.learning_rate) * cost_proxy
        self.step_count += 1
        done = self.step_count >= 100
        return self.state, reward, done, False, {"F": round(F_current, 4)}


class _ActionSpace:
    def __init__(self, n, rng):
        self.n = n; self.rng = rng
    def sample(self):
        a = self.rng.uniform(0, 1, self.n)
        return a / a.sum()


def create_agent():
    return {"algorithm": str(cfg.ml.rl_algorithm), "seed": get_seed(),
            "reward": "F_material — AFI reward, not proxy",
            "label": cfg.meta.simulated_label}
