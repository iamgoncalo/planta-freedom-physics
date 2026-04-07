"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/building_agent.py — Building simulation agent. PlantaOS integration.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed
import numpy as np

def simulate_scenario(scenario: str = "heatwave", hours: int = 8) -> dict:
    """Simulate building scenario. Returns F_global_t trajectory."""
    rng = np.random.default_rng(get_seed())
    ticks_per_hour = 60
    total_ticks = hours * ticks_per_hour
    F_traj = []
    F = float(cfg.building.fem_alert_threshold) + 0.10  # from config: threshold + margin
    for i in range(total_ticks):
        progress = i / total_ticks
        if scenario == "heatwave":
            T = 25 + 17 * progress
            F = max(0.15, F - 0.0003 * max(0, T-26) + rng.normal(0,0.002))
        F_traj.append(round(float(np.clip(F, 0.1, 0.9)), 4))
    alerts = [f"Room_{j}" for j in range(1, hours+1)
              if F_traj[min(j*60-1, total_ticks-1)] < 0.30]
    return {"scenario": scenario, "hours": hours,
            "F_global_t": F_traj,
            "F_global_start": F_traj[0], "F_global_end": F_traj[-1],
            "alerts": alerts,
            "recommendation": "Activate HVAC pre-cooling at hour 3. Reduce occupancy hours 6-8.",
            "label": cfg.meta.simulated_label}
