# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
PlantaOS room F=P/D computation. HORSE CFT SIMULATED. Pintassilgo excluded."""

from __future__ import annotations
import math
from freedom_physics.config import cfg, get_building_weights, get_epsilon
from freedom_physics.core.distortion import (distortion_geometric,
    d_thermal, d_co2, d_humidity, d_light, d_noise, d_occupancy, d_spatial)
from freedom_physics.core.freedom import compute_F, compute_F_global

def compute_room_F(room_id: str, P_spatial: float,
                   temp_c: float, co2_ppm: float, humidity_pct: float,
                   lux: float, noise_db: float, occupants: int,
                   capacity: int, bfs_distance: float,
                   T_setpoint: float | None = None) -> dict:
    """7-channel geometric D. Source: David Fleury HORSE Aveiro emails 3 Mar 2026."""
    th  = cfg.building
    eps = get_epsilon()
    wts = get_building_weights()
    T_sp = T_setpoint if T_setpoint is not None else (
        (float(th.winter_min_c)+float(th.winter_max_c))/2.0)
    channels = {
        "thermal":   d_thermal(temp_c, T_sp, float(th.temp_d_scale)),
        "co2":       d_co2(co2_ppm, float(th.co2_clean_ppm)),
        "humidity":  d_humidity(humidity_pct, float(th.humidity_d_scale)),
        "light":     d_light(lux, float(th.lux_target)),
        "noise":     d_noise(noise_db, float(th.noise_max_db), float(th.noise_d_scale)),
        "occupancy": d_occupancy(occupants, capacity),
        "spatial":   d_spatial(bfs_distance, max(bfs_distance*2, eps)),
    }
    D, attr = distortion_geometric(channels, wts)
    F = compute_F(P_spatial, D)
    alert_level = 0
    if co2_ppm > float(th.co2_alert_ppm): alert_level = max(alert_level,2)
    if co2_ppm > float(th.co2_legal_ppm): alert_level = max(alert_level,4)
    if lux     < float(th.lux_critical):  alert_level = max(alert_level,3)
    if F < 0.35:                          alert_level = max(alert_level,3)
    if F < 0.20:                          alert_level = max(alert_level,4)
    return {
        "room_id":       room_id,
        "F":             round(F,4), "D_total":round(D,4), "P_spatial":round(P_spatial,4),
        "D_channels":    {k:round(v,4) for k,v in channels.items()},
        "D_attribution": {k:round(v,1) for k,v in attr.items()},
        "D_dominant":    max(attr, key=lambda k:attr[k]),
        "alert_level":   alert_level,
        "inputs":        {"temp_c":temp_c,"co2_ppm":co2_ppm,"humidity_pct":humidity_pct,
                          "lux":lux,"noise_db":noise_db,"occupants":occupants,"capacity":capacity},
        "thesis":"T2+T3","label":"SIMULATED",
    }

def compute_building_F(rooms: list[dict]) -> dict:
    "F_global = geometric mean of all room F scores (Deucalion confirmed)."
    F_vals = [r["F"] for r in rooms]
    F_global = compute_F_global(F_vals)
    worst = min(rooms, key=lambda r:r["F"]) if rooms else {}
    alerts = [r for r in rooms if r.get("alert_level",0)>=3]
    return {"F_global":round(F_global,4),"n_rooms":len(rooms),
            "worst_room":worst.get("room_id",""),"worst_F":round(worst.get("F",0),4),
            "alerts":[r["room_id"] for r in alerts],"thesis":"T2+T3","label":"SIMULATED"}


def get_aco_avoid_rooms() -> list:
    """SIMULATED — return rooms ACO must avoid. From config, never hardcoded."""
    from freedom_physics.config import cfg
    return list(cfg.swarm.avoid_rooms)
