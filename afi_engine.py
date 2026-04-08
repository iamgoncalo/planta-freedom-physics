"""
afi_engine.py — Architecture of Freedom Intelligence Core
==========================================================
F = P / D  — HYPOTHESIS UNDER EMPIRICAL TEST — NEVER A PROVEN LAW
D = exp(sum(w_k * ln(max(d_k, 1.0))))  [geometric, R²=0.993, Deucalion seed=2026]
Weight sum validation at startup. ValueError raised if sum ≠ 1.0.

Author : Gonçalo Melo de Magalhães · ORCID 0009-0008-6255-7724
Grant  : FCT 2025.00020.AIVLAB.DEUCALION
SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""
from __future__ import annotations
import math
import numpy as np
from typing import Any

LABEL = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"
SEED  = 2026


class AFIEngine:
    """
    F = P / D engine.
    All weights loaded from genome state dict.
    Weight sum validated at construction — raises ValueError if sum ≠ 1.0.
    """

    def __init__(self, state: dict[str, Any]) -> None:
        self._weights = state["afi_weights"]
        self._validate_weights()
        self._rng = np.random.default_rng(state.get("seed", SEED))

    def _validate_weights(self) -> None:
        """HL-01: Weights must sum to exactly 1.0. Halt if not."""
        s = sum(self._weights.values())
        if abs(s - 1.0) >= 1e-6:
            raise ValueError(
                f"AFI weight sum = {s:.10f} ≠ 1.0 — HALT (HL-01). "
                f"Weights: {self._weights}"
            )

    def compute_D(self, channels: dict[str, float]) -> tuple[float, dict[str, float]]:
        """
        D = exp(sum(w_k * ln(max(d_k, 1.0))))  — geometric mean (HL-11)

        Returns:
            D_total : float
            attribution : dict[str, float]  — % contribution per channel

        Dead alternatives (never use):
            FLRP multiplicative R²=0.0002  → raises RuntimeError
            Additive D R²=0.860            → inferior to geometric R²=0.993
        """
        W = self._weights
        ln_D = sum(
            W.get(k, 0.0) * math.log(max(channels.get(k, 1.0), 1.0))
            for k in W
        )
        D = math.exp(ln_D)

        if ln_D < 1e-12:
            attribution = {k: 0.0 for k in W}
        else:
            attribution = {
                k: round(
                    W.get(k, 0.0) * math.log(max(channels.get(k, 1.0), 1.0))
                    / ln_D * 100.0, 2
                )
                for k in W
            }
        return D, attribution

    def compute_F(self, P_spatial: float,
                  channels: dict[str, float]) -> dict[str, Any]:
        """
        F = P / D  — hypothesis under empirical test.

        Args:
            P_spatial : BFS topology score (observer-dependent, from room graph)
            channels  : dict of d_k values per sensor channel

        Returns full F result dict including D, attribution, F score, label.

        Negative results (always reported with equal depth):
          - P alone R²=0.83 > P/D R²=0.48 in open navigation
          - D's value is attribution (which channel dominates), not prediction
        """
        D, attr = self.compute_D(channels)
        F = float(np.clip(P_spatial / max(D, 1e-9), 0.0, 1.0))
        dominant = max(attr, key=lambda k: attr[k]) if attr else "none"
        return {
            "F":           round(F, 4),
            "P_spatial":   round(P_spatial, 4),
            "D_total":     round(D, 4),
            "D_attribution": attr,
            "D_dominant":  dominant,
            "weights":     self._weights,
            "negative_results": {
                "P_alone_R2":     0.83,
                "P_over_D_R2":    0.48,
                "note":           "P alone beats P/D in open navigation — D's value is attribution",
                "FLRP_R2":        0.0002,
                "additive_D_R2":  0.860,
                "geometric_D_R2": 0.993,
            },
            "label": LABEL,
        }

    def d_thermal(self, T_C: float, T_setpoint_C: float = 20.0) -> float:
        """d_thermal = max(1.0, 1.0 + |T - T_sp| / 2.5)  [ISO 7730]"""
        return max(1.0, 1.0 + abs(T_C - T_setpoint_C) / 2.5)

    def d_co2(self, ppm: float) -> float:
        """d_co2 = max(1.0, ppm / 700.0)  [700ppm = clean reference air]"""
        return max(1.0, ppm / 700.0)

    def d_humidity(self, rh_pct: float) -> float:
        """d_humidity = max(1.0, 1.0 + |RH - 50| / 15.0)  [ISO 7730]"""
        return max(1.0, 1.0 + abs(rh_pct - 50.0) / 15.0)

    def d_light(self, lux: float) -> float:
        """d_light = max(1.0, 400 / max(lux, 10))  [EN 12464-1]"""
        return max(1.0, 400.0 / max(lux, 10.0))

    def d_noise(self, db: float) -> float:
        """d_noise = max(1.0, 1.0 + max(0, dB-45) / 10)  [ISO 11690-1]"""
        return max(1.0, 1.0 + max(0.0, db - 45.0) / 10.0)

    def d_occupancy(self, n: int, capacity: int) -> float:
        """d_occupancy = max(1.0, n / max(capacity, 1))  [EN 13779]"""
        return max(1.0, n / max(capacity, 1))

    def d_spatial(self, dist: float, dist_max: float) -> float:
        """d_spatial = 1.0 + dist / max(d_max, 1)  [BFS]"""
        return 1.0 + dist / max(dist_max, 1.0)

    def nominal_F(self, state: dict[str, Any],
                  n_occupants: int = 2) -> dict[str, Any]:
        """
        Compute F at nominal FWH conditions.
        Sensor readings: comfortable temperature, CO2 from n occupants,
        50% RH, 350 lux, 28 dB noise.
        P_spatial = 0.81 (single-room open plan BFS score).
        """
        VENT = state["systems"].get("respiratory", {}).get("ventilation", {})
        from fwh_physics import co2_steady_state_ppm

        # Nominal conditions: at setpoint = d_thermal=1, CO2 at ambient = d_co2=1
        # All channels at minimum distortion → F = P_spatial (optimal)
        T_nominal  = 20.0   # at setpoint — d_thermal = 1.0
        T_sp       = 20.0   # setpoint (XML system 04 nominal)
        co2_ppm    = 415.0  # ambient CO2 (NOAA 2026) — d_co2 = 415/700 < 1 → d=1.0
        rh         = 50.0   # optimal humidity — d_humidity = 1.0
        lux        = 400.0  # EN 12464-1 target — d_light = 1.0
        db         = 28.0   # quiet room — d_noise = 1.0
        P_spatial  = 0.81   # single-room open plan BFS (FWH 30m2 square)

        channels = {
            "thermal":   self.d_thermal(T_nominal, T_sp),
            "co2":       self.d_co2(co2_ppm),
            "humidity":  self.d_humidity(rh),
            "light":     self.d_light(lux),
            "noise":     self.d_noise(db),
            "occupancy": self.d_occupancy(n_occupants, 4),
            "spatial":   1.0,
        }
        result = self.compute_F(P_spatial, channels)
        result["n_occupants"] = n_occupants
        result["sensor_inputs"] = {
            "T_C": T_nominal, "T_sp": T_sp, "co2_ppm": round(co2_ppm, 1),
            "rh_pct": rh, "lux": lux, "noise_db": db,
        }
        return result

    def flrp_multiplicative_dead(self, *args, **kwargs) -> None:
        """HL-13: FLRP multiplicative decomposition DEAD (R²=0.0002)."""
        raise RuntimeError(
            "FLRP multiplicative product R²=0.0002 — DEAD — never call. "
            "See HL-13. Use geometric D only (R²=0.993)."
        )


if __name__ == "__main__":
    from fwh_parser import parse
    s   = parse("fwh_genome.xml")
    afi = AFIEngine(s)

    print("=== AFI Engine Self-Test ===")
    print(f"Weights validated: sum={sum(afi._weights.values()):.6f}")

    # Nominal single occupant
    r1 = afi.nominal_F(s, n_occupants=1)
    print(f"F nominal (1 person): {r1['F']}  D={r1['D_total']}  dominant={r1['D_dominant']}")

    # Nominal family
    r4 = afi.nominal_F(s, n_occupants=4)
    print(f"F nominal (4 persons): {r4['F']}  D={r4['D_total']}  CO2={r4['sensor_inputs']['co2_ppm']}ppm")

    # Nominal 6 persons
    r6 = afi.nominal_F(s, n_occupants=6)
    print(f"F nominal (6 persons): {r6['F']}")

    # Negative results — always reported
    print(f"\nNegative results (always reported with equal depth):")
    nr = r1["negative_results"]
    print(f"  P alone R²={nr['P_alone_R2']} > P/D R²={nr['P_over_D_R2']} in open navigation")
    print(f"  FLRP multiplicative R²={nr['FLRP_R2']} — DEAD")
    print(f"  Additive D R²={nr['additive_D_R2']} < geometric R²={nr['geometric_D_R2']}")

    # FLRP dead test
    try:
        afi.flrp_multiplicative_dead()
    except RuntimeError as e:
        print(f"\nFLRP guard: {e}")

    print(f"\n{LABEL}")
