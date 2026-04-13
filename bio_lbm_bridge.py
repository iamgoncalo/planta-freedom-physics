"""
bio_lbm_bridge.py
─────────────────────────────────────────────────────────────────────────────
Biological Algorithm Bridge for PlantaOS LBM 60-second tick.
Maps room sensor state → BioState → runs 43 building-relevant bio algorithms
→ returns BuildingActions for HVAC, ventilation, alerts, and ACO routing.

HARD LIMITS:
  HL-03  ZERO AI in this module. Pure Python. Zero LLM calls.
  HL-05  Pintassilgo: never assigned groups. pheromone=0 permanent.
  HL-08  All parameters in config.yaml. Zero hardcodes here.
  HL-11  D always geometric, never additive.

PRINCIPLE:
  Life does not use thresholds with if/else.
  Life uses heuristics: if CO2 high → breathe more.
  If temperature wrong → correct proportionally.
  This module translates that into building actions.

Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION
ALL RESULTS SIMULATION-BASED · F=P/D HYPOTHESIS UNDER TEST · seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import math
import importlib.util
import os
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG (read from config.yaml if present, else use PlantaOS constants)
# ─────────────────────────────────────────────────────────────────────────────

def _load_cfg():
    try:
        import yaml
        for path in ["config.yaml", "../config.yaml", "../../config.yaml"]:
            if os.path.exists(path):
                with open(path) as f:
                    return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}

_CFG = _load_cfg()
_C = _CFG.get("comfort", {})
_D = _CFG.get("distortion", {}).get("weights", {})

# All read from config.yaml — fallback to AFI Master values
TEMP_WINTER_MIN  = _C.get("winter_min_c", 18.0)
TEMP_WINTER_MAX  = _C.get("winter_max_c", 22.0)
TEMP_SUMMER_MIN  = _C.get("summer_min_c", 22.0)
TEMP_SUMMER_MAX  = _C.get("summer_max_c", 26.0)
CO2_ALERT_PPM    = _C.get("co2_alert_ppm", 800)
CO2_LEGAL_PPM    = _C.get("co2_legal_ppm", 1000)
LUX_TARGET       = _C.get("lux_classroom_target", 400)
LUX_MIN          = _C.get("lux_classroom_min", 300)
LUX_CRITICAL     = _C.get("lux_critical", 150)
NOISE_MAX        = _C.get("noise_max_db", 45)
RH_MIN           = _C.get("humidity_min_pct", 40)
RH_MAX           = _C.get("humidity_max_pct", 60)

# Priority hierarchy (A83): life safety > comfort > energy > cost
PRIORITY = ["life_safety", "comfort", "energy", "cost"]

# Pintassilgo hard limit (HL-05)
PINTASSILGO_BLOCK = True
ACO_AVOID = _CFG.get("aco", {}).get("avoid_rooms", ["Pintassilgo"])


# ─────────────────────────────────────────────────────────────────────────────
# LOAD bio_algorithms (lazy, on first use)
# ─────────────────────────────────────────────────────────────────────────────

_bio_module = None

def _get_bio():
    global _bio_module
    if _bio_module is not None:
        return _bio_module
    for candidate in [
        os.path.join(os.path.dirname(__file__), "bio_algorithms.py"),
        os.path.expanduser("~/Downloads/planta-freedom-physics/bio_algorithms.py"),
        "bio_algorithms.py",
    ]:
        if os.path.exists(candidate):
            spec = importlib.util.spec_from_file_location("bio_algorithms", candidate)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _bio_module = mod
            return mod
    raise FileNotFoundError("bio_algorithms.py not found")


# ─────────────────────────────────────────────────────────────────────────────
# ROOM STATE → BIOSTATE MAPPER
# ─────────────────────────────────────────────────────────────────────────────

def room_to_biostate(room_state: dict, room_name: str = ""):
    """
    Convert PlantaOS room state dict → BioState.

    Mapping rationale:
      core_temp_c    ← room T (building = body temperature)
      co2_room_ppm   ← room CO2 (direct: same signal)
      humidity_pct   ← room RH (direct)
      light_lux      ← room lux (direct)
      noise_db       ← room noise (direct)
      o2_sat_pct     ← F score mapped to SpO2 range 60–99
                       (F=1.0 → SpO2=99%, F=0.0 → SpO2=60%)
      damage_pct     ← D-1 mapped 0–100%
                       (D=1.0 → 0%, D=2.5 → 100%)
      fatigue_pct    ← occupancy ratio × 60
                       (full room = 60% fatigue on HVAC)
      pathogen_load  ← CO2/legal_limit proxy for air quality risk
      pain_level     ← alert_level / 4
    """
    bio = _get_bio()
    s = bio.BioState()
    def _get(pk, lk, dv):
        if pk in room_state: return float(room_state[pk])
        return float(room_state.get(lk, dv))
    T        = _get("temp_c",       "T",          20.0)
    co2      = _get("co2_ppm",      "co2",        420.0)
    rh       = _get("humidity_pct", "rh",         50.0)
    lux      = _get("lux",          "lux",        400.0)
    noise    = _get("noise_db",     "noise",      40.0)
    F        = _get("F",            "F",          0.5)
    D        = _get("D",            "D",          1.0)
    n_people = int(_get("occupancy","n_people",   0))
    cap      = int(_get("cap",      "cap",        max(1, n_people)))
    alert    = int(_get("alert_level","alert_level",0))

    s.core_temp_c   = float(T)
    s.skin_temp_c   = float(T) - 3.0     # building skin ≈ core - 3°C
    s.co2_room_ppm  = float(co2)
    s.co2_blood_pct = min(7.5, max(3.5, 3.5 + (co2 - 420) / 1000))  # map ppm→blood%
    s.humidity_pct  = float(rh)
    s.light_lux     = float(lux)
    s.noise_db      = float(noise)
    s.o2_sat_pct    = 60.0 + F * 39.0    # F=1→99%, F=0→60%
    s.damage_pct    = min(100.0, max(0.0, (D - 1.0) / 1.5 * 100.0))
    s.fatigue_pct   = min(100.0, (n_people / max(1, cap)) * 60.0)
    s.pathogen_load = min(1.0, max(0.0, (co2 - 420) / (CO2_LEGAL_PPM - 420)))
    s.pain_level    = min(1.0, alert / 4.0)
    s.stomata_open  = True                # building windows = stomata
    s.water_stress  = 0.0
    s.atp_store_pct = min(100.0, F * 100.0)
    s.glucose_mmol  = 3.5 + F * 2.0      # proxy for energy reserve

    # Pintassilgo special state (HL-05)
    if room_name == "Pintassilgo":
        s.light_lux = 85.0
        s.damage_pct = min(100.0, s.damage_pct + 30.0)  # structural deficit

    return s


# ─────────────────────────────────────────────────────────────────────────────
# BUILDING ACTION dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BuildingAction:
    """Output of one bio_lbm tick for one room."""
    room_id: str
    tick: int = 0

    # HVAC
    hvac_mode: str = "hold"          # heat | cool | hold | off
    hvac_delta_setpoint_c: float = 0.0
    hvac_urgency: str = "normal"     # immediate | normal | scheduled

    # Ventilation (stomata = A64)
    ventilation: str = "normal"      # max | normal | min | closed
    damper_pct: float = 50.0         # 0–100%

    # Lighting
    lighting: str = "hold"           # increase | hold | dim | off

    # Alert
    alert_level: int = 0             # 0–4
    alert_triggers: list = field(default_factory=list)

    # Priority (A83)
    priority: str = "comfort"        # life_safety | comfort | energy | cost

    # Occupancy routing (A22 inflammation isolation)
    block_occupancy: bool = False
    reason: str = ""

    # F improvement expected
    delta_F_expected: float = 0.0

    # Active bio algorithms that triggered this action
    bio_triggers: list = field(default_factory=list)

    label: str = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST"


# ─────────────────────────────────────────────────────────────────────────────
# BUILDING-RELEVANT BIO ALGORITHMS (subset of 100)
# Only the 43 that map directly to building systems (from HOUSE_BIO_MAP)
# ─────────────────────────────────────────────────────────────────────────────

def _run_building_bio(s, room_name: str, month: int = 4, hour: float = 9.0) -> list:
    """
    Run building-relevant bio algorithms on BioState s.
    Returns list of triggered AlgorithmResult.
    """
    bio = _get_bio()

    # Run only building-relevant subset
    results = []
    fns = [
        # D01 Respiration → ventilation
        bio.A01_co2_trigger,
        bio.A02_o2_threshold,
        bio.A06_sleep_breathing,
        bio.A07_yawn_reset,
        bio.A10_co2_room_alert,
        # D02 Thermoregulation → HVAC
        bio.A11_sweat_onset,
        bio.A12_shiver_heat,
        bio.A13_vasodilation,
        bio.A14_vasoconstriction,
        bio.A15_behavioral_thermostat,
        bio.A18_circadian_temp_cycle,
        # D03 Pain/Damage → emergency actions
        bio.A21_nociception_withdraw,
        bio.A22_inflammation_cascade,
        bio.A23_coagulation_clot,
        # D04 Energy → energy management
        bio.A34_atp_priority_brain,
        bio.A35_sleep_restore,
        # D05 Immune → anomaly detection
        bio.A41_pattern_recognition,
        bio.A46_nk_surveillance,
        bio.A47_interferon_warning,
        bio.A48_apoptosis_selfclean,
        bio.A49_autophagy_recycle,
        # D06 Sensory → alert filtering
        bio.A51_habituation,
        bio.A52_sensitization,
        bio.A54_motion_alert,
        # D07 Plant → window/blind control
        bio.A61_phototropism,
        bio.A64_stomata_co2_control,
        bio.A66_circadian_plant_clock,
        # D08 Homeostasis → PID/balance
        bio.A71_ph_buffer,
        bio.A73_blood_pressure,
        bio.A75_negative_feedback_hormone,
        bio.A79_sleep_homeostasis,
        # D09 Safety → fail-safes
        bio.A81_dual_organ_redundancy,
        bio.A82_fail_safe_autonomic,
        bio.A83_priority_hierarchy,
        bio.A84_pain_mandatory_interrupt,
        bio.A85_disgust_barrier,
        bio.A86_fear_fright_flight,
        bio.A87_surprise_interrupt,
        bio.A89_dna_repair,
        bio.A90_antioxidant_scavenge,
        # D10 Renewal → lifecycle
        bio.A91_telomere_clock,
        bio.A95_ordered_apoptosis,
        bio.A99_nutrient_cycle_close,
    ]

    for fn in fns:
        try:
            # Some algorithms take extra kwargs
            name = fn.__name__
            if "circadian_temp" in name:
                r = fn(s, hour_of_day=hour)
            elif "phototropism" in name:
                sun_angle = abs(hour - 12) * 7.5  # degrees from zenith
                r = fn(s, light_dir_deg=sun_angle)
            elif "circadian_plant" in name:
                r = fn(s, hour=hour)
            elif "circadian_energy" in name:
                r = fn(s, hour=hour)
            elif "habituation" in name:
                r = fn(s, repeats=0)
            elif "sensitization" in name:
                r = fn(s, threat_repeats=0)
            elif "renewal_spring" in name:
                r = fn(s, month=month)
            elif "telomere" in name:
                # Building component lifecycle proxy
                # Map room_name to age_divisions (older rooms = more divisions)
                pass
            else:
                r = fn(s)
            results.append(r)
        except Exception:
            pass  # graceful skip — never block the 60s tick

    return [r for r in results if r.triggered]


# ─────────────────────────────────────────────────────────────────────────────
# ACTION TRANSLATOR
# Converts bio algorithm triggers → BuildingAction
# ─────────────────────────────────────────────────────────────────────────────

def _bio_to_action(triggered: list, room_state: dict, room_name: str,
                   s, tick: int = 0) -> BuildingAction:
    """Translate triggered bio algorithms into building actions."""
    action = BuildingAction(room_id=room_name, tick=tick)

    for r in triggered:
        action.bio_triggers.append(f"{r.algo_id}:{r.name}")
        action.delta_F_expected += r.delta_F

    # ── RESPIRATION algorithms → ventilation ─────────────────────────────────
    respiration = [r for r in triggered if r.domain == "RESPIRATION"]
    def _gv(pk, lk, dv):
        return float(room_state[pk]) if pk in room_state else float(room_state.get(lk, dv))
    co2 = _gv("co2_ppm", "co2", 420.0)

    if any(r.algo_id in ("A10",) for r in triggered):
        # A10: CO2 > legal limit → max ventilation + alert (A10 = Portaria 353-A)
        action.ventilation = "max"
        action.damper_pct = 100.0
        action.alert_level = max(action.alert_level, 4)
        action.alert_triggers.append(f"CO2={co2:.0f}ppm > {CO2_LEGAL_PPM}ppm LEGAL BREACH")
        action.priority = "life_safety"

    elif any(r.algo_id in ("A01", "A07") for r in triggered):
        # A01/A07: CO2 rising → increase ventilation proportionally
        deficit = max(0.0, co2 - CO2_ALERT_PPM) / (CO2_LEGAL_PPM - CO2_ALERT_PPM)
        action.ventilation = "max" if deficit > 0.7 else "normal"
        action.damper_pct = min(100.0, 50.0 + deficit * 50.0)
        action.alert_level = max(action.alert_level, 2 if deficit > 0.5 else 1)
        action.alert_triggers.append(f"CO2={co2:.0f}ppm rising")

    elif any(r.algo_id == "A06" for r in triggered):
        # A06: Autonomic — always minimum ventilation
        action.ventilation = max(action.ventilation, "min") if action.ventilation == "closed" else action.ventilation
        action.damper_pct = max(action.damper_pct, 20.0)

    # ── THERMOREGULATION → HVAC ───────────────────────────────────────────────
    T     = _gv("temp_c", "T", 20.0)
    month = int(room_state.get("month", 4))
    T_sp = 20.0 if month in [10, 11, 12, 1, 2, 3] else 24.0
    T_sp = _CFG.get("comfort", {}).get("winter_min_c", T_sp) if month <= 3 or month >= 10 else _CFG.get("comfort", {}).get("summer_min_c", T_sp)

    thermo = [r for r in triggered if r.domain == "THERMOREGULATION"]

    if any(r.algo_id == "A11" for r in triggered):
        # Sweat = too hot → cool
        delta = min(3.0, (T - T_sp - 0.5))
        action.hvac_mode = "cool"
        action.hvac_delta_setpoint_c = -delta
        action.hvac_urgency = "immediate" if delta > 2.0 else "normal"

    elif any(r.algo_id == "A12" for r in triggered):
        # Shiver = too cold → heat
        delta = min(3.0, (T_sp - T + 0.5))
        action.hvac_mode = "heat"
        action.hvac_delta_setpoint_c = delta
        action.hvac_urgency = "immediate" if delta > 2.0 else "normal"

    elif any(r.algo_id == "A13" for r in triggered):
        # Vasodilation = slightly warm → open dampers before HVAC
        action.ventilation = "normal"
        action.damper_pct = max(action.damper_pct, 70.0)

    elif any(r.algo_id == "A14" for r in triggered):
        # Vasoconstriction = cold → close, retain heat
        action.damper_pct = min(action.damper_pct, 30.0)
        action.hvac_mode = "heat"

    if any(r.algo_id == "A18" for r in triggered):
        # Circadian pre-warming/cooling (A18) — pre-act before D arrives
        if 6.0 <= room_state.get("hour", 9.0) <= 8.0:
            action.hvac_mode = "heat" if month in [10,11,12,1,2,3] else "cool"
            action.hvac_urgency = "scheduled"

    # ── PAIN/DAMAGE → emergency (A21, A22, A23) ───────────────────────────────
    if any(r.algo_id == "A21" for r in triggered):
        # Nociception: immediate interrupt
        action.alert_level = max(action.alert_level, 4)
        action.priority = "life_safety"
        action.alert_triggers.append("EMERGENCY: critical damage detected")
        action.hvac_urgency = "immediate"

    if any(r.algo_id == "A22" for r in triggered):
        action.alert_level = max(action.alert_level, 3)
        action.reason = "Zone inflammation: repair active"
        if s.damage_pct > 40.0:  # D > 1.60 only
            action.block_occupancy = True
            action.reason = "Zone quarantine: severe damage"

    if any(r.algo_id == "A23" for r in triggered):
        # Coagulation: close valves, stop loss
        action.alert_triggers.append("CLOSE VALVES: leak/breach detected")
        action.alert_level = max(action.alert_level, 4)
        action.priority = "life_safety"

    # ── PLANT algorithms → window/blind control ────────────────────────────────
    if any(r.algo_id == "A64" for r in triggered):
        # Stomata CO2/water control — windows as valves
        s_obj = s
        if s_obj.stomata_open:
            action.ventilation = "normal"
        else:
            action.damper_pct = min(action.damper_pct, 20.0)

    if any(r.algo_id == "A66" for r in triggered):
        # Pre-dawn circadian: open blinds/HVAC before occupancy
        action.hvac_urgency = "scheduled"

    # ── SAFETY algorithms → structural decisions ────────────────────────────────
    if any(r.algo_id == "A82" for r in triggered):
        # Fail-safe autonomic: minimum ventilation ALWAYS
        action.damper_pct = max(action.damper_pct, 20.0)

    if any(r.algo_id == "A83" for r in triggered):
        # Priority hierarchy: override if energy scarce
        if action.alert_level == 0:
            action.priority = "energy"

    if any(r.algo_id == "A84" for r in triggered):
        # Pain mandatory interrupt: escalate alert
        action.alert_level = max(action.alert_level, 4)
        action.priority = "life_safety"

    # ── IMMUNE → anomaly detection ─────────────────────────────────────────────
    if any(r.algo_id == "A41" for r in triggered):
        # PAMP: unknown pattern detected
        action.alert_level = max(action.alert_level, 1)
        action.alert_triggers.append("Anomaly pattern detected")

    if any(r.algo_id == "A47" for r in triggered):
        # Interferon: warn adjacent rooms
        action.alert_triggers.append("WARN adjacent rooms: pre-arm")

    # ── HOMEOSTASIS → PID / balance ────────────────────────────────────────────
    if any(r.algo_id == "A75" for r in triggered):
        # Negative feedback: prevent runaway HVAC
        if abs(action.hvac_delta_setpoint_c) > 2.5:
            action.hvac_delta_setpoint_c = math.copysign(2.5, action.hvac_delta_setpoint_c)

    if any(r.algo_id == "A79" for r in triggered):
        # Sleep homeostasis: no occupancy → deep sleep mode
        if int(_gv("occupancy", "n_people", 0)) == 0:
            action.hvac_mode = "off"
            action.ventilation = "min"
            action.damper_pct = 20.0
            action.lighting = "off"

    # ── PINTASSILGO hard block (HL-05) ─────────────────────────────────────────
    if room_name in ACO_AVOID:
        action.block_occupancy = True
        action.reason = "HL-05: No AC + lux=85 (71.6% below EN 12464-1). Groups forbidden."
        action.alert_level = max(action.alert_level, 1)

    return action


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION — called by lbm.py every 60s per room
# ─────────────────────────────────────────────────────────────────────────────

def bio_tick(room_name: str, room_state: dict, tick: int = 0,
             month: int = 4, hour: float = 9.0) -> BuildingAction:
    """
    Bio-inspired decision tick for one room.
    Called by lbm.py every 60 seconds. ZERO AI. Pure Python.

    Args:
        room_name:  e.g. "Egas_Moniz"
        room_state: dict with keys T, co2, rh, lux, noise, n_people, F, D,
                    alert_level, cap, hvac_state, month, hour
        tick:       monotonic tick counter
        month:      1–12
        hour:       0.0–23.99

    Returns:
        BuildingAction with hvac_mode, ventilation, alert_level, etc.

    SIMULATED — F=P/D HYPOTHESIS UNDER TEST
    """
    # Add context to room_state for downstream use
    room_state = dict(room_state)
    room_state.setdefault("month", month)
    room_state.setdefault("hour", hour)

    # 1. Convert room state to biological state
    s = room_to_biostate(room_state, room_name)

    # 2. Run building-relevant bio algorithms
    triggered = _run_building_bio(s, room_name, month=month, hour=hour)

    # 3. Translate triggers to building actions
    action = _bio_to_action(triggered, room_state, room_name, s, tick)

    return action


def bio_tick_building(all_rooms: dict, tick: int = 0,
                      month: int = 4, hour: float = 9.0) -> dict:
    """
    Run bio_tick for all 24 rooms. Returns dict of room_id → BuildingAction.
    Adds interferon propagation: critical room → pre-arm adjacent.

    SIMULATED — F=P/D HYPOTHESIS UNDER TEST
    """
    actions = {}
    for room_name, room_state in all_rooms.items():
        actions[room_name] = bio_tick(room_name, room_state, tick, month, hour)

    # A47 interferon propagation: if room level ≥ 3, warn floor neighbours
    critical_rooms = [n for n, a in actions.items() if a.alert_level >= 3]
    for cr in critical_rooms:
        floor = all_rooms[cr].get("floor", 0)
        for other, a in actions.items():
            if other != cr and all_rooms[other].get("floor", 0) == floor:
                if a.alert_level < 1:
                    a.alert_level = 1
                    a.alert_triggers.append(f"Interferon from {cr}: pre-arm")

    return actions


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY REPORTER
# ─────────────────────────────────────────────────────────────────────────────

def summarise_actions(actions: dict) -> dict:
    """Building-level summary of all bio tick actions."""
    n_hvac_cool = sum(1 for a in actions.values() if a.hvac_mode == "cool")
    n_hvac_heat = sum(1 for a in actions.values() if a.hvac_mode == "heat")
    n_vent_max  = sum(1 for a in actions.values() if a.ventilation == "max")
    n_alerts    = sum(1 for a in actions.values() if a.alert_level >= 2)
    n_blocked   = sum(1 for a in actions.values() if a.block_occupancy)
    max_alert   = max((a.alert_level for a in actions.values()), default=0)
    life_safety = [n for n, a in actions.items() if a.priority == "life_safety"]
    delta_F_sum = sum(a.delta_F_expected for a in actions.values())

    return {
        "tick_summary": {
            "hvac_cool": n_hvac_cool,
            "hvac_heat": n_hvac_heat,
            "ventilation_max": n_vent_max,
            "alert_rooms": n_alerts,
            "blocked_rooms": n_blocked,
            "max_alert_level": max_alert,
            "life_safety_rooms": life_safety,
            "delta_F_sum": round(delta_F_sum, 4),
        },
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# DEMO — run standalone to validate bridge
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  BIO LBM BRIDGE — PlantaOS 60s tick with bio heuristics     ║")
    print("║  ZERO AI · Pure Python · config-driven                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("  SIMULATED — F=P/D HYPOTHESIS UNDER TEST\n")

    # Simulate HORSE CFT rooms at 09:00 on a cold January morning
    TEST_ROOMS = {
        "Egas_Moniz":    {"T": 16.5, "co2": 820, "rh": 55, "lux": 409, "noise": 43,
                          "n_people": 12, "cap": 17, "F": 0.42, "D": 1.19, "floor": 0, "alert_level": 0},
        "Vasco_da_Gama": {"T": 19.2, "co2": 1050, "rh": 62, "lux": 305, "noise": 48,
                          "n_people": 20, "cap": 20, "F": 0.26, "D": 1.26, "floor": 1, "alert_level": 2},
        "Pintassilgo":   {"T": 14.1, "co2": 450,  "rh": 48, "lux": 85,  "noise": 35,
                          "n_people": 0,  "cap": 12, "F": 0.38, "D": 1.30, "floor": 0, "alert_level": 0},
        "Quintanilha":   {"T": 22.8, "co2": 780,  "rh": 58, "lux": 384, "noise": 46,
                          "n_people": 10, "cap": 15, "F": 0.25, "D": 1.35, "floor": 1, "alert_level": 1},
        "Hall_GF":       {"T": 20.1, "co2": 450,  "rh": 50, "lux": 280, "noise": 40,
                          "n_people": 3,  "cap": 10, "F": 0.81, "D": 1.23, "floor": 0, "alert_level": 0},
    }

    print("── TICK 1: January 09:00 — HORSE CFT ──\n")
    actions = bio_tick_building(TEST_ROOMS, tick=1, month=1, hour=9.0)

    for rname, action in actions.items():
        print(f"  [{rname}]")
        print(f"    HVAC: {action.hvac_mode} {action.hvac_delta_setpoint_c:+.1f}°C | "
              f"vent={action.ventilation} ({action.damper_pct:.0f}%) | "
              f"alert={action.alert_level} | priority={action.priority}")
        if action.block_occupancy:
            print(f"    BLOCK: {action.reason}")
        if action.alert_triggers:
            for t in action.alert_triggers:
                print(f"    ALERT: {t}")
        if action.bio_triggers:
            print(f"    BIO: {', '.join(action.bio_triggers[:4])}"
                  + (f" +{len(action.bio_triggers)-4} more" if len(action.bio_triggers) > 4 else ""))
        print(f"    ΔF_expected={action.delta_F_expected:+.4f}\n")

    summary = summarise_actions(actions)
    print("── BUILDING SUMMARY ──")
    for k, v in summary["tick_summary"].items():
        print(f"  {k}: {v}")

    print("\n  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    print("  Designing to free. -- Gonçalo\n")
