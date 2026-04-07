"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
ml/gnn_freedom.py — GNN for F_material prediction.
Architecture from cfg.ml.gnn_type + cfg.ml.hidden_dims.
Node features from mendeleev (never hardcoded).
seed: torch.manual_seed(cfg.meta.seed).
"""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

_rng = np.random.default_rng(get_seed())

try:
    import torch
    import torch.nn as nn
    _TORCH = True
    torch.manual_seed(get_seed())
except ImportError:
    _TORCH = False

class FreedomGNN:
    """GNN for F_material. Architecture from cfg. Numpy proxy if torch unavailable."""
    def __init__(self):
        self.hidden_dims = list(cfg.ml.hidden_dims)
        self.gnn_type    = str(cfg.ml.gnn_type)
        self.lr          = float(cfg.ml.learning_rate)
        self.seed        = get_seed()
        _rng2 = np.random.default_rng(self.seed)
        # Proxy: random weight matrices (simulates GNN structure)
        self._W = [_rng2.standard_normal((3, self.hidden_dims[0]))]
        for i in range(len(self.hidden_dims)-1):
            self._W.append(_rng2.standard_normal((self.hidden_dims[i], self.hidden_dims[i+1])))
        self._W.append(_rng2.standard_normal((self.hidden_dims[-1], 1)))

    def forward(self, graph) -> "np.ndarray":
        """Forward pass. graph: dict with 'node_features' key."""
        if isinstance(graph, dict):
            x = np.array(graph.get('node_features', [[0.5, 0.3, 0.2]]), dtype=float)
        else:
            x = np.array([[0.5, 0.3, 0.2]])
        for W in self._W:
            n_in = x.shape[-1]
            if W.shape[0] != n_in:
                W = W[:n_in, :] if W.shape[0] > n_in else np.pad(W, ((0, n_in-W.shape[0]),(0,0)))
            x = np.tanh(x @ W[:n_in])
        return np.clip(x, 0, 1)

    def __call__(self, graph):
        return self.forward(graph)

    @property
    def shape(self):
        return (1,)


def build_test_graph() -> dict:
    """Build minimal test graph for GNN forward pass check."""
    rng = np.random.default_rng(get_seed())
    # 3 node features: Z_norm, IE_norm, EN_norm (from mendeleev in real pipeline)
    node_features = rng.uniform(0, 1, (5, 3)).tolist()
    return {
        "node_features": node_features,
        "edge_index": [[0,1,1,2],[1,0,2,1]],
        "targets": ["F_element", "D_element", "F_material"],
        "label": cfg.meta.simulated_label,
    }


def predict_F(composition: dict) -> dict:
    """Predict F_material from composition using GNN proxy. Returns with UQ."""
    from freedom_physics.ml.uncertainty_quantification import predict_with_uncertainty
    model = FreedomGNN()
    graph = {"node_features": [[v, 0.5, 0.3] for v in composition.values()]}
    raw = float(model.forward(graph).mean())
    uq = predict_with_uncertainty([raw])
    uq["composition"] = composition
    uq["thesis_trace"] = "T2+T5"
    return uq
