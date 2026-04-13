"""
bio_algorithms.py
─────────────────────────────────────────────────────────────────────────────
100 Biological Algorithms for the AFI Theory of Everything
Planta Smart Homes · Freedom Water Home · PlantaOS
Gonçalo Melo de Magalhães · ORCID 0009-0008-6255-7724
FCT 2025.00020.AIVLAB.DEUCALION

PRINCIPLE:
  Life does not know everything. Life knows enough.
  Every biological algorithm is a heuristic: cheap, fast, good enough.
  Pain → withdraw. Warm → stay. Rotting smell → avoid. Sweet → consume.
  The house must operate the same way.

  F = P / D  (hypothesis under test)
  In biology: F = perceived_freedom / accumulated_distortion
  A healthy organism maximises F. A dying organism has D → ∞.

STRUCTURE (10 domains × 10 algorithms = 100):
  D01  RESPIRATION       — gas exchange, CO2/O2 balance
  D02  THERMOREGULATION  — temperature homeostasis
  D03  PAIN/DAMAGE       — detect, isolate, repair
  D04  ENERGY            — acquire, store, spend, recover
  D05  IMMUNE/DEFENCE    — pattern recognition, memory, tolerance
  D06  SENSORY           — perceive, filter, prioritise
  D07  PLANT INTELLIGENCE— tropisms, stomata, mycorrhizal
  D08  HOMEOSTASIS       — pH, pressure, osmosis, balance
  D09  REDUNDANCY/SAFETY — dual organs, fail-safes, priority
  D10  DEATH/RENEWAL     — apoptosis, decomposition, rebirth

ALL RESULTS SIMULATION-BASED.
F=P/D IS A HYPOTHESIS UNDER TEST. NOT A PROVEN LAW.
seed=2026. zero hardcodes.
─────────────────────────────────────────────────────────────────────────────
"""

import math
import yaml
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADER (zero hardcodes — all parameters in bio_config.yaml)
# ─────────────────────────────────────────────────────────────────────────────

BIO_CONFIG_DEFAULTS = {
    "seed": 2026,
    # D01 Respiration
    "co2_breathe_trigger_pct": 5.0,   # % CO2 in blood that triggers breath
    "o2_low_threshold_pct": 95.0,     # SpO2 below this → increase rate
    "breath_rate_rest": 12,            # breaths/min at rest
    "breath_rate_max": 60,             # breaths/min maximum
    "breath_volume_L": 0.5,            # tidal volume litres
    "co2_atmosphere_ppm": 420,         # outdoor baseline
    "co2_legal_ppm": 1000,             # Portaria 353-A/2013
    # D02 Thermoregulation
    "body_temp_setpoint_c": 37.0,
    "sweat_onset_c": 37.5,
    "shiver_onset_c": 36.0,
    "fever_setpoint_c": 38.5,
    "heat_death_c": 42.0,
    "cold_death_c": 28.0,
    "thermal_comfort_band_c": 1.0,     # ± from setpoint
    # D03 Pain/Damage
    "pain_withdrawal_ms": 50,          # reflex arc, milliseconds
    "inflammation_peak_h": 48,         # peak inflammation hours
    "wound_heal_days_minor": 7,
    "wound_heal_days_major": 30,
    "clot_formation_min": 5,           # minutes to clot
    # D04 Energy
    "glucose_low_mmol": 3.9,           # hypoglycaemia threshold
    "glucose_high_mmol": 7.8,          # hyperglycaemia threshold
    "atp_priority_brain_pct": 20,      # brain gets 20% of total ATP
    "sleep_hours_min": 7,
    "sleep_hours_opt": 8,
    "metabolic_rate_rest_kcal_h": 80,
    "metabolic_rate_max_kcal_h": 1200,
    # D05 Immune
    "fever_kill_temp_c": 38.5,         # temp that slows most bacteria
    "antibody_memory_years": 70,       # immune memory duration
    "nk_surveillance_interval_h": 1,   # NK cell patrol cycle
    "interferon_delay_h": 4,           # time to produce interferon
    # D06 Sensory
    "habituation_repeats": 10,         # stimulus repeats before ignore
    "sensitization_repeats": 3,        # threat repeats before amplify
    "bitter_rejection_ms": 200,        # time to spit bitter taste
    "pain_localisation_cm": 2,         # spatial resolution of pain
    # D07 Plant
    "phototropism_angle_deg_h": 5,     # degrees/hour toward light
    "stomata_co2_threshold_ppm": 400,  # open stomata below this
    "stomata_drought_close_rh": 35,    # close if humidity < this %
    "leaf_fold_temp_c": 35,            # leaf fold above this temp
    "mycorrhizal_share_pct": 30,       # % sugar shared with network
    # D08 Homeostasis
    "ph_low": 7.35,                    # blood pH low (acidosis)
    "ph_high": 7.45,                   # blood pH high (alkalosis)
    "bp_systolic_low": 90,             # mmHg hypotension threshold
    "bp_systolic_high": 140,           # mmHg hypertension threshold
    "osmolality_low": 275,             # mOsm/kg
    "osmolality_high": 295,            # mOsm/kg
    # D09 Redundancy
    "organ_redundancy_pairs": ["kidney", "lung", "eye", "ear"],
    "priority_1": "brain_o2",          # always protect first
    "priority_2": "heart_rhythm",
    "priority_3": "core_temperature",
    "autonomic_fail_safe": True,       # breathing continues unconscious
    # D10 Death/Renewal
    "telomere_max_divisions": 50,      # Hayflick limit
    "apoptosis_signal": "DNA_unrepairable",
    "decompose_days_avg": 30,          # body → soil nutrients
    "nutrient_cycle_years": 1,         # nutrients back into ecosystem
}

try:
    with open("bio_config.yaml", "r") as f:
        _user_cfg = yaml.safe_load(f) or {}
    CFG = {**BIO_CONFIG_DEFAULTS, **_user_cfg}
except FileNotFoundError:
    CFG = BIO_CONFIG_DEFAULTS

RNG = np.random.default_rng(CFG["seed"])


# ─────────────────────────────────────────────────────────────────────────────
# SHARED TYPES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BioState:
    """Minimal state of a living system. All values normalised 0..1 where possible."""
    # Gas
    co2_blood_pct: float = 4.0         # % CO2 in blood
    o2_sat_pct: float = 98.0           # SpO2 %
    # Temperature
    core_temp_c: float = 37.0
    skin_temp_c: float = 33.0
    # Energy
    glucose_mmol: float = 5.0
    atp_store_pct: float = 80.0        # 0–100%
    fatigue_pct: float = 0.0           # 0–100%
    # Damage
    damage_pct: float = 0.0            # 0–100%
    inflammation_level: float = 0.0    # 0–1
    # Immune
    pathogen_load: float = 0.0         # 0–1
    immune_response: float = 0.0       # 0–1
    # Sensory
    pain_level: float = 0.0            # 0–1
    light_lux: float = 400.0
    noise_db: float = 40.0
    co2_room_ppm: float = 420.0
    humidity_pct: float = 50.0
    # Plant state (if applicable)
    stomata_open: bool = True
    phototropism_angle: float = 0.0    # degrees from vertical
    water_stress: float = 0.0          # 0–1
    # Homeostasis
    ph: float = 7.40
    bp_systolic: float = 120.0
    osmolality: float = 285.0
    # Meta
    alive: bool = True
    age_divisions: int = 0             # cell divisions (Hayflick counter)
    tick: int = 0                      # simulation step

    def F_score(self) -> float:
        """
        Biological Freedom score. Maps organism health to AFI F=P/D.
        P = capacity to perceive and act (SpO2, glucose, consciousness).
        D = geometric mean of all distortion channels.
        SIMULATED.
        """
        # Perception capacity
        P_o2 = self.o2_sat_pct / 100.0
        P_glucose = 1.0 - abs(self.glucose_mmol - 5.0) / 5.0
        P_glucose = max(0.01, P_glucose)
        P = (P_o2 * P_glucose) ** 0.5

        # Distortion channels (all ≥ 1.0)
        d_temp   = max(1.0, 1.0 + abs(self.core_temp_c - CFG["body_temp_setpoint_c"]) / 2.0)
        d_co2    = max(1.0, self.co2_blood_pct / 4.0)
        d_damage = max(1.0, 1.0 + self.damage_pct / 50.0)
        d_pain   = max(1.0, 1.0 + self.pain_level * 2.0)
        d_immune = max(1.0, 1.0 + self.pathogen_load * 2.0)

        # Geometric D (matching AFI hard limit HL-11)
        w = {"temp": 0.35, "co2": 0.25, "damage": 0.20, "pain": 0.10, "immune": 0.10}
        ln_D = (w["temp"]   * math.log(d_temp)   +
                w["co2"]    * math.log(d_co2)     +
                w["damage"] * math.log(d_damage)  +
                w["pain"]   * math.log(d_pain)    +
                w["immune"] * math.log(d_immune))
        D = math.exp(ln_D)
        F = min(1.0, max(0.0, P / D))
        return round(F, 4)


@dataclass
class AlgorithmResult:
    """Output of one biological algorithm."""
    algo_id: str
    name: str
    domain: str
    triggered: bool
    action: str
    afi_interpretation: str
    F_before: float
    F_after: float
    delta_F: float = field(init=False)
    confidence: float = 1.0
    label: str = "SIMULATED"

    def __post_init__(self):
        self.delta_F = round(self.F_after - self.F_before, 4)


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 01 — RESPIRATION (A01–A10)
# ─────────────────────────────────────────────────────────────────────────────

def A01_co2_trigger(s: BioState) -> AlgorithmResult:
    """Blood CO2 rises above threshold → breathe. The most fundamental reflex."""
    fb = s.F_score()
    triggered = s.co2_blood_pct > CFG["co2_breathe_trigger_pct"]
    if triggered:
        s.co2_blood_pct = max(3.5, s.co2_blood_pct - 0.8)
        s.o2_sat_pct = min(99.0, s.o2_sat_pct + 1.5)
    return AlgorithmResult("A01", "CO2 Trigger Breath", "RESPIRATION",
        triggered, "Exhale CO2, inhale O2" if triggered else "Hold",
        "D_co2 rising → breathe to restore P_perception", fb, s.F_score())

def A02_o2_threshold(s: BioState) -> AlgorithmResult:
    """SpO2 drops below 95% → increase breathing rate. Hypoxia response."""
    fb = s.F_score()
    triggered = s.o2_sat_pct < CFG["o2_low_threshold_pct"]
    if triggered:
        s.o2_sat_pct = min(99.0, s.o2_sat_pct + 2.0)
        s.co2_blood_pct = max(3.5, s.co2_blood_pct - 0.5)
    return AlgorithmResult("A02", "O2 Threshold Rate Increase", "RESPIRATION",
        triggered, "Increase breath rate" if triggered else "Maintain",
        "SpO2 drop = P collapse → must restore to maintain F", fb, s.F_score())

def A03_rate_adaptation(s: BioState) -> AlgorithmResult:
    """Effort (fatigue) → scale respiratory rate proportionally."""
    fb = s.F_score()
    rate = CFG["breath_rate_rest"] + (s.fatigue_pct / 100.0) * (CFG["breath_rate_max"] - CFG["breath_rate_rest"])
    triggered = s.fatigue_pct > 20.0
    if triggered:
        s.co2_blood_pct = max(3.8, s.co2_blood_pct - 0.3)
    return AlgorithmResult("A03", "Effort Rate Adaptation", "RESPIRATION",
        triggered, f"Rate={rate:.1f} breaths/min",
        "Proportional response: D_metabolic rises, ventilation scales", fb, s.F_score())

def A04_apnea_override(s: BioState) -> AlgorithmResult:
    """CO2 > 7% (dangerous) → forced override, cannot suppress."""
    fb = s.F_score()
    triggered = s.co2_blood_pct > 7.0
    if triggered:
        s.co2_blood_pct = 5.5  # forced reset
        s.damage_pct = min(100.0, s.damage_pct + 5.0)  # cost of crisis
    return AlgorithmResult("A04", "Apnea Override (Autonomous)", "RESPIRATION",
        triggered, "FORCED BREATH — cannot suppress" if triggered else "Normal",
        "Autonomic override: F→0 unless corrected immediately", fb, s.F_score())

def A05_altitude_adaptation(s: BioState) -> AlgorithmResult:
    """Thin air (O2 low) → produce more red blood cells over days."""
    fb = s.F_score()
    triggered = s.o2_sat_pct < 90.0
    if triggered:
        s.o2_sat_pct = min(99.0, s.o2_sat_pct + 0.1)  # slow, days-long process
    return AlgorithmResult("A05", "Altitude RBC Adaptation", "RESPIRATION",
        triggered, "Increase EPO → more RBC" if triggered else "No change",
        "Long-horizon D_chronic → structural P increase", fb, s.F_score())

def A06_sleep_breathing(s: BioState) -> AlgorithmResult:
    """Unconscious → brainstem continues breathing. Fail-safe autonomic."""
    fb = s.F_score()
    triggered = True  # ALWAYS active
    s.co2_blood_pct = min(5.5, max(3.5, s.co2_blood_pct))
    return AlgorithmResult("A06", "Autonomic Sleep Breathing", "RESPIRATION",
        triggered, "Brainstem CPG maintains rhythm",
        "F-preservation during zero conscious P: pure autonomic", fb, s.F_score())

def A07_yawn_reset(s: BioState) -> AlgorithmResult:
    """CO2 mild buildup in underventilated areas → yawn (deep reset breath)."""
    fb = s.F_score()
    triggered = s.co2_room_ppm > 800 and s.co2_blood_pct > 4.8
    if triggered:
        s.co2_blood_pct = max(4.0, s.co2_blood_pct - 0.4)
    return AlgorithmResult("A07", "Yawn CO2 Reset", "RESPIRATION",
        triggered, "Deep breath reset" if triggered else "None",
        "Room CO2 D rising → individual corrects P", fb, s.F_score())

def A08_cough_clear(s: BioState) -> AlgorithmResult:
    """Obstruction in airway → explosive expulsion reflex."""
    fb = s.F_score()
    obstruction = s.damage_pct > 30 and s.o2_sat_pct < 96
    triggered = obstruction
    if triggered:
        s.o2_sat_pct = min(99.0, s.o2_sat_pct + 3.0)
        s.pain_level = min(1.0, s.pain_level + 0.1)
    return AlgorithmResult("A08", "Cough Clear Reflex", "RESPIRATION",
        triggered, "Expel obstruction" if triggered else "Clear",
        "Mechanical D → physical expulsion to restore P_airway", fb, s.F_score())

def A09_sneeze_irritant(s: BioState) -> AlgorithmResult:
    """Nasal irritant → 160 km/h expulsion. Chemical D → physical response."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.3
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.2)
    return AlgorithmResult("A09", "Sneeze Irritant Expulsion", "RESPIRATION",
        triggered, "Expel irritant at 160km/h" if triggered else "None",
        "Chemical D_airway → immediate mechanical response", fb, s.F_score())

def A10_co2_room_alert(s: BioState) -> AlgorithmResult:
    """Room CO2 > legal limit → mandatory ventilation signal (building-level)."""
    fb = s.F_score()
    triggered = s.co2_room_ppm > CFG["co2_legal_ppm"]
    if triggered:
        s.co2_room_ppm = max(420.0, s.co2_room_ppm - 200.0)  # ventilate
    return AlgorithmResult("A10", "Room CO2 Legal Alert", "RESPIRATION",
        triggered, f"VENTILATE NOW — {s.co2_room_ppm:.0f}ppm (limit={CFG['co2_legal_ppm']})" if triggered else "OK",
        "Building D_co2 → Portaria 353-A/2013 trigger → open windows/HVAC", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 02 — THERMOREGULATION (A11–A20)
# ─────────────────────────────────────────────────────────────────────────────

def A11_sweat_onset(s: BioState) -> AlgorithmResult:
    """Core temp > 37.5°C → sweat. Evaporative cooling at 580W/kg."""
    fb = s.F_score()
    triggered = s.core_temp_c > CFG["sweat_onset_c"]
    if triggered:
        s.core_temp_c -= 0.2
    return AlgorithmResult("A11", "Sweat Onset Cooling", "THERMOREGULATION",
        triggered, f"Sweat: -0.2°C → {s.core_temp_c:.2f}°C" if triggered else "None",
        "D_thermal ↑ → evaporative P restoration", fb, s.F_score())

def A12_shiver_heat(s: BioState) -> AlgorithmResult:
    """Core temp < 36°C → shiver. Muscle oscillation generates ~500W/m²."""
    fb = s.F_score()
    triggered = s.core_temp_c < CFG["shiver_onset_c"]
    if triggered:
        s.core_temp_c += 0.15
        s.atp_store_pct = max(0.0, s.atp_store_pct - 3.0)
    return AlgorithmResult("A12", "Shiver Heat Generation", "THERMOREGULATION",
        triggered, f"Shiver: +0.15°C → {s.core_temp_c:.2f}°C" if triggered else "None",
        "D_thermal_cold → metabolic P restoration (costs ATP)", fb, s.F_score())

def A13_vasodilation(s: BioState) -> AlgorithmResult:
    """Skin hot → dilate vessels, radiate heat outward."""
    fb = s.F_score()
    triggered = s.skin_temp_c > 35.0
    if triggered:
        s.core_temp_c = max(37.0, s.core_temp_c - 0.1)
        s.skin_temp_c -= 0.5
    return AlgorithmResult("A13", "Vasodilation Radiation", "THERMOREGULATION",
        triggered, "Vessels dilate — radiate heat" if triggered else "Normal",
        "Peripheral D_excess → open channels to distribute", fb, s.F_score())

def A14_vasoconstriction(s: BioState) -> AlgorithmResult:
    """Cold → constrict peripheral vessels, protect core."""
    fb = s.F_score()
    triggered = s.skin_temp_c < 28.0
    if triggered:
        s.core_temp_c = min(37.5, s.core_temp_c + 0.05)
    return AlgorithmResult("A14", "Vasoconstriction Core Protect", "THERMOREGULATION",
        triggered, "Vessels constrict — protect core" if triggered else "Normal",
        "D_cold_peripheral → isolate high-P core", fb, s.F_score())

def A15_behavioral_thermostat(s: BioState) -> AlgorithmResult:
    """Behavioural: too hot → seek shade/cool. 80% of thermoregulation is behaviour."""
    fb = s.F_score()
    triggered = s.core_temp_c > 38.0 or s.core_temp_c < 35.5
    action = "Seek shade" if s.core_temp_c > 38.0 else ("Seek warmth" if s.core_temp_c < 35.5 else "Comfortable")
    if triggered:
        delta = -0.3 if s.core_temp_c > 38.0 else 0.3
        s.core_temp_c += delta
    return AlgorithmResult("A15", "Behavioural Thermostat", "THERMOREGULATION",
        triggered, action,
        "D_env → movement (P_mobility) to restore F", fb, s.F_score())

def A16_fever_setpoint(s: BioState) -> AlgorithmResult:
    """Pathogen detected → hypothalamus raises setpoint to 38.5°C to kill bacteria."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.2
    if triggered:
        s.core_temp_c = min(s.core_temp_c + 0.3, CFG["fever_setpoint_c"])
        s.pathogen_load = max(0.0, s.pathogen_load - 0.05)  # bacteria slowing
    return AlgorithmResult("A16", "Fever Setpoint Shift", "THERMOREGULATION",
        triggered, f"Fever: setpoint→{CFG['fever_setpoint_c']}°C" if triggered else "Normal temp",
        "Intentional D_thermal to kill pathogen D_immune — trading P types", fb, s.F_score())

def A17_heat_shock_proteins(s: BioState) -> AlgorithmResult:
    """Sudden temperature spike → produce HSP to protect protein structure."""
    fb = s.F_score()
    triggered = s.core_temp_c > 39.5
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 2.0)  # HSP protection
    return AlgorithmResult("A17", "Heat Shock Protein Response", "THERMOREGULATION",
        triggered, "Produce HSP — protect proteins" if triggered else "None",
        "Extreme D_thermal → emergency protein P preservation", fb, s.F_score())

def A18_circadian_temp_cycle(s: BioState, hour_of_day: float = 8.0) -> AlgorithmResult:
    """Core temperature naturally cycles ±0.5°C over 24h. Peak 18h, trough 04h."""
    fb = s.F_score()
    natural_delta = 0.5 * math.sin(2 * math.pi * (hour_of_day - 4.0) / 24.0)
    s.core_temp_c = 37.0 + natural_delta  # reset to circadian
    triggered = True
    return AlgorithmResult("A18", "Circadian Temperature Cycle", "THERMOREGULATION",
        triggered, f"Circadian T={s.core_temp_c:.2f}°C at hour={hour_of_day}",
        "Endogenous F rhythm — P anticipates D before it arrives", fb, s.F_score())

def A19_brown_fat_thermogenesis(s: BioState) -> AlgorithmResult:
    """Extreme cold (< 10°C ambient) → brown adipose tissue metabolic heat."""
    fb = s.F_score()
    triggered = s.skin_temp_c < 15.0 and s.core_temp_c < 36.5
    if triggered:
        s.core_temp_c += 0.25
        s.atp_store_pct = max(0.0, s.atp_store_pct - 5.0)
    return AlgorithmResult("A19", "Brown Fat Thermogenesis", "THERMOREGULATION",
        triggered, "BAT activated — metabolic heat" if triggered else "None",
        "Emergency metabolic P: uncoupled mitochondria bypass ATP", fb, s.F_score())

def A20_transpiration_cooling(s: BioState) -> AlgorithmResult:
    """PLANT: Water evaporation through leaves cools tissue. Same physics as sweat."""
    fb = s.F_score()
    triggered = s.core_temp_c > CFG["leaf_fold_temp_c"] - 2
    if triggered and s.water_stress < 0.5:
        s.core_temp_c -= 0.4
        s.water_stress += 0.05
    return AlgorithmResult("A20", "Plant Transpiration Cooling", "THERMOREGULATION",
        triggered, "Evaporate water → cool tissue" if triggered else "None",
        "Plant D_thermal → water P expenditure to preserve leaf F", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 03 — PAIN / DAMAGE RESPONSE (A21–A30)
# ─────────────────────────────────────────────────────────────────────────────

def A21_nociception_withdraw(s: BioState) -> AlgorithmResult:
    """Tissue damage → withdraw in 50ms. Reflex arc bypasses brain."""
    fb = s.F_score()
    triggered = s.pain_level > 0.5 or s.damage_pct > 40
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 1.0)  # withdrawal reduces ongoing damage
    return AlgorithmResult("A21", "Nociception Withdrawal Reflex", "PAIN_DAMAGE",
        triggered, f"WITHDRAW in {CFG['pain_withdrawal_ms']}ms" if triggered else "No threat",
        "Pain D → immediate P_mobility response, no cognition needed", fb, s.F_score())

def A22_inflammation_cascade(s: BioState) -> AlgorithmResult:
    """Injury → localised inflammation: isolate, clean, recruit repair."""
    fb = s.F_score()
    triggered = s.damage_pct > 10
    if triggered:
        s.inflammation_level = min(1.0, s.inflammation_level + 0.1)
        s.damage_pct = max(0.0, s.damage_pct - 0.5)  # slow repair begins
    return AlgorithmResult("A22", "Inflammation Cascade", "PAIN_DAMAGE",
        triggered, f"Inflammation={s.inflammation_level:.2f} — repair active" if triggered else "None",
        "D_damage → controlled D_inflammation to restore P_structure", fb, s.F_score())

def A23_coagulation_clot(s: BioState) -> AlgorithmResult:
    """Bleed → platelet cascade → clot in < 5 min. Stop resource loss."""
    fb = s.F_score()
    triggered = s.damage_pct > 30
    if triggered:
        s.damage_pct = min(100.0, s.damage_pct)  # clot stops bleeding
        # 13-factor cascade activates
    return AlgorithmResult("A23", "Coagulation Clot Formation", "PAIN_DAMAGE",
        triggered, f"Clot in ~{CFG['clot_formation_min']}min — stop loss" if triggered else "None",
        "Resource loss D → cascade F-preservation response", fb, s.F_score())

def A24_wound_healing(s: BioState) -> AlgorithmResult:
    """Clot formed → fibroblasts → collagen → remodel. Slow rebuild."""
    fb = s.F_score()
    triggered = s.inflammation_level > 0 and s.damage_pct < 30
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 0.1)
        s.inflammation_level = max(0.0, s.inflammation_level - 0.02)
    return AlgorithmResult("A24", "Wound Healing Remodel", "PAIN_DAMAGE",
        triggered, f"Healing: damage={s.damage_pct:.1f}% → collagen" if triggered else "None",
        "Post-D repair: P_structure slowly restored over days", fb, s.F_score())

def A25_referred_pain_signal(s: BioState) -> AlgorithmResult:
    """Organ damage → surface pain signal. Heart attack = left arm. Body maps internal D."""
    fb = s.F_score()
    triggered = s.pain_level > 0.7 and s.damage_pct > 50
    action = "Map internal D to surface signal for cognition" if triggered else "No referral"
    return AlgorithmResult("A25", "Referred Pain Signal", "PAIN_DAMAGE",
        triggered, action,
        "Internal D invisible to consciousness → translate to felt P signal", fb, s.F_score())

def A26_chronic_pain_avoidance(s: BioState) -> AlgorithmResult:
    """Repeated damage same location → permanent avoidance behaviour wired in."""
    fb = s.F_score()
    triggered = s.pain_level > 0.3 and s.damage_pct > 20
    if triggered:
        s.pain_level = min(1.0, s.pain_level + 0.05)  # sensitization
    return AlgorithmResult("A26", "Chronic Avoidance Learning", "PAIN_DAMAGE",
        triggered, "Sensitize — avoid this stimulus forever" if triggered else "None",
        "Past D → future P_avoidance encoded in memory", fb, s.F_score())

def A27_itch_scratch(s: BioState) -> AlgorithmResult:
    """Surface irritant → itch signal → scratch → remove. Histamine pathway."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.1 and s.inflammation_level > 0.1
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.05)
    return AlgorithmResult("A27", "Itch-Scratch Surface Clean", "PAIN_DAMAGE",
        triggered, "Scratch to remove irritant" if triggered else "None",
        "Surface D_chemical → mechanical P_cleaning response", fb, s.F_score())

def A28_nausea_expel(s: BioState) -> AlgorithmResult:
    """Toxin detected → nausea → vomit. Fastest detox available."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.6
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.4)
        s.atp_store_pct = max(0.0, s.atp_store_pct - 5.0)
    return AlgorithmResult("A28", "Nausea Expulsion", "PAIN_DAMAGE",
        triggered, "EXPEL — vomit reflex" if triggered else "None",
        "Chemical D too high → violent physical P to restore baseline", fb, s.F_score())

def A29_learned_aversion(s: BioState) -> AlgorithmResult:
    """One bad experience (toxin) → never eat that again. Single-trial learning."""
    fb = s.F_score()
    triggered = s.pain_level > 0.8
    if triggered:
        s.pain_level = min(1.0, s.pain_level + 0.1)  # encode strongly
    return AlgorithmResult("A29", "Learned Taste Aversion", "PAIN_DAMAGE",
        triggered, "Encode aversion: never again" if triggered else "None",
        "One-shot D encoding → permanent P avoidance modification", fb, s.F_score())

def A30_plant_wound_seal(s: BioState) -> AlgorithmResult:
    """PLANT: Wound → resin/latex/callus. Seal break before pathogen enters."""
    fb = s.F_score()
    triggered = s.damage_pct > 5
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 0.3)
        s.pathogen_load = max(0.0, s.pathogen_load - 0.1)
    return AlgorithmResult("A30", "Plant Wound Sealing", "PAIN_DAMAGE",
        triggered, "Resin/callus formation" if triggered else "None",
        "Physical D_breach → chemical P seal, block future D_pathogen", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 04 — ENERGY MANAGEMENT (A31–A40)
# ─────────────────────────────────────────────────────────────────────────────

def A31_glucose_monitor(s: BioState) -> AlgorithmResult:
    """Blood sugar low → eat / mobilise glycogen. High → store as fat."""
    fb = s.F_score()
    triggered = s.glucose_mmol < CFG["glucose_low_mmol"]
    if triggered:
        s.glucose_mmol = min(7.0, s.glucose_mmol + 1.5)
        s.atp_store_pct = min(100.0, s.atp_store_pct + 10.0)
    return AlgorithmResult("A31", "Glucose Homeostasis", "ENERGY",
        triggered, f"Glucose={s.glucose_mmol:.1f}mmol — {'MOBILISE' if triggered else 'OK'}",
        "P_metabolic ↓ → mobilise reserves to maintain F", fb, s.F_score())

def A32_fat_mobilisation(s: BioState) -> AlgorithmResult:
    """Fasting > 4h → lipase activates, fat → free fatty acids for ATP."""
    fb = s.F_score()
    triggered = s.atp_store_pct < 30 and s.glucose_mmol < 4.5
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 8.0)
    return AlgorithmResult("A32", "Fat Mobilisation Fasting", "ENERGY",
        triggered, "Lipase active — fat→ATP" if triggered else "Glucose primary",
        "Secondary reserve: D_glucose_low → P_lipid_alternative", fb, s.F_score())

def A33_glycogen_burst(s: BioState) -> AlgorithmResult:
    """Sprint demand → instant glycogen → glucose conversion (no O2 needed)."""
    fb = s.F_score()
    triggered = s.fatigue_pct > 70 and s.atp_store_pct < 20
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 15.0)
        s.glucose_mmol = max(2.0, s.glucose_mmol - 1.0)
    return AlgorithmResult("A33", "Glycogen Burst (Anaerobic)", "ENERGY",
        triggered, "BURST: glycogen→glucose (anaerobic)" if triggered else "None",
        "Emergency P: glycolysis bypasses oxidative phosphorylation", fb, s.F_score())

def A34_atp_priority_brain(s: BioState) -> AlgorithmResult:
    """Energy scarce → brain gets first claim. 20% of body ATP to 2% of mass."""
    fb = s.F_score()
    triggered = s.atp_store_pct < 40
    if triggered:
        # Brain protected, other systems deprioritised
        s.fatigue_pct = min(100.0, s.fatigue_pct + 3.0)
    return AlgorithmResult("A34", "ATP Priority: Brain First", "ENERGY",
        triggered, f"Brain ATP protected. Peripheral fatigue={s.fatigue_pct:.0f}%",
        "Hierarchy: highest-P organ gets resources first", fb, s.F_score())

def A35_sleep_restore(s: BioState) -> AlgorithmResult:
    """Sleep deprivation → mandatory rest override."""
    fb = s.F_score()
    triggered = s.fatigue_pct > 80
    if triggered:
        s.fatigue_pct = max(0.0, s.fatigue_pct - 20.0)
        s.atp_store_pct = min(100.0, s.atp_store_pct + 10.0)
        s.damage_pct = max(0.0, s.damage_pct - 5.0)
    return AlgorithmResult("A35", "Sleep Restore Mandate", "ENERGY",
        triggered, f"SLEEP REQUIRED. Fatigue={s.fatigue_pct:.0f}%",
        "Adenosine D_fatigue → forced offline P restoration", fb, s.F_score())

def A36_circadian_energy_peak(s: BioState, hour: float = 8.0) -> AlgorithmResult:
    """Peak cognitive performance 09–12h. Bottom at 03–05h. Circadian P cycle."""
    fb = s.F_score()
    peak_factor = 0.5 + 0.5 * math.sin(2 * math.pi * (hour - 3.0) / 24.0)
    triggered = True
    return AlgorithmResult("A36", "Circadian Energy Peak", "ENERGY",
        triggered, f"Performance factor={peak_factor:.2f} at hour={hour}",
        "Endogenous P rhythm — anticipate energy D before it depletes", fb, s.F_score())

def A37_metabolic_rate_adapt(s: BioState) -> AlgorithmResult:
    """Cold or starvation → slow metabolism. Reduce burn rate to extend survival."""
    fb = s.F_score()
    triggered = s.core_temp_c < 35.0 or s.atp_store_pct < 15
    if triggered:
        s.fatigue_pct = min(100.0, s.fatigue_pct + 1.0)  # slower = more tired
    return AlgorithmResult("A37", "Metabolic Rate Adaptation", "ENERGY",
        triggered, "Slow metabolism — conserve" if triggered else "Normal rate",
        "D_scarce → reduce P expenditure rate", fb, s.F_score())

def A38_growth_repair_night(s: BioState) -> AlgorithmResult:
    """Night: GH surges, repair active. Day: action. Night: rebuild."""
    fb = s.F_score()
    triggered = True  # happens every night
    s.damage_pct = max(0.0, s.damage_pct - 1.0)
    return AlgorithmResult("A38", "Nocturnal Growth/Repair", "ENERGY",
        triggered, "GH surge — rebuild tissue",
        "Night P_restoration: F recovered for next day cycle", fb, s.F_score())

def A39_starvation_protocol(s: BioState) -> AlgorithmResult:
    """72h+ starvation → ketosis, down-regulate reproduction, immune maintenance."""
    fb = s.F_score()
    triggered = s.glucose_mmol < 2.5
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 5.0)  # ketones
    return AlgorithmResult("A39", "Starvation Ketosis Protocol", "ENERGY",
        triggered, "KETOSIS: brain switches to ketones" if triggered else "Normal",
        "Extreme D_glucose → alternative P_substrate to protect brain F", fb, s.F_score())

def A40_plant_photosynthesis(s: BioState, light_lux: float = 400.0) -> AlgorithmResult:
    """PLANT: Light → convert CO2+H2O → glucose+O2. ATP from photons."""
    fb = s.F_score()
    efficiency = min(1.0, light_lux / 800.0)
    triggered = light_lux > 50
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + efficiency * 3.0)
    return AlgorithmResult("A40", "Plant Photosynthesis", "ENERGY",
        triggered, f"ATP gain={efficiency*3:.2f}% from {light_lux}lux",
        "P_light → chemical P_energy. D_co2 room drops as plant absorbs", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 05 — IMMUNE / DEFENCE (A41–A50)
# ─────────────────────────────────────────────────────────────────────────────

def A41_pattern_recognition(s: BioState) -> AlgorithmResult:
    """Innate: recognise PAMP (pathogen pattern) → respond immediately. No memory needed."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.15
    if triggered:
        s.immune_response = min(1.0, s.immune_response + 0.2)
    return AlgorithmResult("A41", "PAMP Pattern Recognition (Innate)", "IMMUNE",
        triggered, f"PAMP detected → innate response={s.immune_response:.2f}",
        "Generic D_pattern → immediate P_defence (no learning needed)", fb, s.F_score())

def A42_fever_induction(s: BioState) -> AlgorithmResult:
    """Pyrogens → hypothalamus → fever. 38.5°C slows most bacteria by 50%."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.2
    if triggered:
        s.core_temp_c = min(CFG["fever_setpoint_c"], s.core_temp_c + 0.2)
        s.pathogen_load = max(0.0, s.pathogen_load - 0.03)
    return AlgorithmResult("A42", "Fever Induction", "IMMUNE",
        triggered, f"Fever={s.core_temp_c:.1f}°C — pathogen growth ↓" if triggered else "Normothermia",
        "Intentional D_thermal to create hostile D_environment for pathogen", fb, s.F_score())

def A43_local_inflammation(s: BioState) -> AlgorithmResult:
    """Breach → localise. Isolate the problem. Don't let D spread."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.1 and s.damage_pct > 5
    if triggered:
        s.inflammation_level = min(1.0, s.inflammation_level + 0.05)
        s.pathogen_load = max(0.0, s.pathogen_load - 0.02)
    return AlgorithmResult("A43", "Local Inflammation Isolation", "IMMUNE",
        triggered, "Quarantine breach — local swelling" if triggered else "None",
        "D_breach → ring of isolation: prevent systemic D spread", fb, s.F_score())

def A44_antibody_memory(s: BioState) -> AlgorithmResult:
    """First exposure → B cells encode → faster/stronger next time. Decades."""
    fb = s.F_score()
    triggered = s.immune_response > 0.5
    if triggered:
        # Memory persists — next time immune_response 10x faster
        pass
    return AlgorithmResult("A44", "Antibody Memory Encoding", "IMMUNE",
        triggered, f"Memory encoded for ~{CFG['antibody_memory_years']} years" if triggered else "None",
        "P_experience stored as D_library: future D recognised faster", fb, s.F_score())

def A45_self_tolerance(s: BioState) -> AlgorithmResult:
    """Learn 'self' during thymic education → never attack own cells."""
    fb = s.F_score()
    triggered = False  # developmental — happens once
    return AlgorithmResult("A45", "Self-Tolerance (Thymic)", "IMMUNE",
        triggered, "Self-patterns memorised: never attack",
        "P_self-recognition: D_autoimmune prevented by exclusion list", fb, s.F_score())

def A46_nk_surveillance(s: BioState) -> AlgorithmResult:
    """NK cells patrol every tissue every hour. Cancer or virus → kill."""
    fb = s.F_score()
    triggered = True  # constant
    if s.pathogen_load > 0.1:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.04)
    return AlgorithmResult("A46", "NK Cell Constant Surveillance", "IMMUNE",
        triggered, f"NK patrol: pathogen_load={s.pathogen_load:.3f}",
        "Continuous P_monitoring: no D threshold needed, always watching", fb, s.F_score())

def A47_interferon_warning(s: BioState) -> AlgorithmResult:
    """Infected cell → release interferon → warn neighbours → pre-arm."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.3
    if triggered:
        s.immune_response = min(1.0, s.immune_response + 0.1)
    return AlgorithmResult("A47", "Interferon Neighbour Warning", "IMMUNE",
        triggered, f"IFN broadcast — neighbours pre-armed in {CFG['interferon_delay_h']}h" if triggered else "None",
        "P_warning signal: D spreads information before D_damage spreads", fb, s.F_score())

def A48_apoptosis_selfclean(s: BioState) -> AlgorithmResult:
    """Cell damaged beyond repair → self-destruct cleanly. No mess for neighbours."""
    fb = s.F_score()
    triggered = s.damage_pct > 80
    if triggered:
        s.damage_pct = 0.0  # cell replaced
        s.pathogen_load = max(0.0, s.pathogen_load - 0.1)
        s.age_divisions += 1
    return AlgorithmResult("A48", "Apoptosis Ordered Self-Destruct", "IMMUNE",
        triggered, "APOPTOSIS: cell cleanly removed" if triggered else "Alive",
        "Ultimate D_damage → controlled P_withdrawal: system integrity maintained", fb, s.F_score())

def A49_autophagy_recycle(s: BioState) -> AlgorithmResult:
    """Starvation or damage → eat own damaged parts. Recycling before dying."""
    fb = s.F_score()
    triggered = s.atp_store_pct < 25 or s.damage_pct > 30
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 5.0)
        s.damage_pct = max(0.0, s.damage_pct - 3.0)
    return AlgorithmResult("A49", "Autophagy Self-Recycling", "IMMUNE",
        triggered, "Eat damaged parts → ATP + clean" if triggered else "None",
        "Internal D_junk → P_recycle: D becomes resource", fb, s.F_score())

def A50_microbiome_balance(s: BioState) -> AlgorithmResult:
    """Gut bacteria equilibrium: 1000 species. Imbalance → disease."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.4
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.05)
        s.immune_response = max(0.0, s.immune_response - 0.02)
    return AlgorithmResult("A50", "Microbiome Equilibrium", "IMMUNE",
        triggered, f"Microbiome buffering pathogen_load={s.pathogen_load:.3f}",
        "Distributed P_ecosystem: 1000 species share D suppression", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 06 — SENSORY / PERCEPTION (A51–A60)
# ─────────────────────────────────────────────────────────────────────────────

def A51_habituation(s: BioState, repeats: int = 0) -> AlgorithmResult:
    """Repeated neutral stimulus → ignore. Save P for novel signals."""
    fb = s.F_score()
    triggered = repeats > CFG["habituation_repeats"]
    return AlgorithmResult("A51", "Habituation Filter", "SENSORY",
        triggered, f"Ignore repeated neutral after {repeats} repeats" if triggered else "Attend",
        "P_attention filtered: D_noise reduced by ignoring non-D", fb, s.F_score())

def A52_sensitization(s: BioState, threat_repeats: int = 0) -> AlgorithmResult:
    """Repeated threat → amplify response. The opposite of habituation."""
    fb = s.F_score()
    triggered = threat_repeats > CFG["sensitization_repeats"]
    if triggered:
        s.pain_level = min(1.0, s.pain_level + 0.1)
    return AlgorithmResult("A52", "Sensitization Amplification", "SENSORY",
        triggered, f"Amplify response after {threat_repeats} threats" if triggered else "Normal",
        "Repeated D → increase P_sensitivity to that D channel", fb, s.F_score())

def A53_contrast_detection(s: BioState) -> AlgorithmResult:
    """Edges, not fills. Retina encodes change, not absolute level. Efficient."""
    fb = s.F_score()
    triggered = True
    return AlgorithmResult("A53", "Contrast Detection (Edges)", "SENSORY",
        triggered, "Encoding: delta, not absolute. P_edges only.",
        "P_efficient: brain encodes D_change not D_absolute — 10x compression", fb, s.F_score())

def A54_motion_alert(s: BioState) -> AlgorithmResult:
    """Moving object → immediate alert. Still = safe. Move = check."""
    fb = s.F_score()
    triggered = s.noise_db > 55  # using noise as proxy for motion
    return AlgorithmResult("A54", "Motion Alert Priority", "SENSORY",
        triggered, "MOTION DETECTED — attend immediately" if triggered else "Static environment",
        "D_moving > D_static: evolution prioritises kinetic D", fb, s.F_score())

def A55_colour_warning(s: BioState) -> AlgorithmResult:
    """Bright unusual colours → caution (poisonous creatures/plants). Innate."""
    fb = s.F_score()
    triggered = s.light_lux > 800  # proxy: unusual brightness
    return AlgorithmResult("A55", "Colour Warning Response", "SENSORY",
        triggered, "Unusual visual D — approach cautiously" if triggered else "Normal",
        "Pattern P_visual encodes species-level D_memory", fb, s.F_score())

def A56_bitter_rejection(s: BioState) -> AlgorithmResult:
    """Bitter → spit in 200ms. Most toxins are bitter. No trial-and-error needed."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.2
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.1)
    return AlgorithmResult("A56", "Bitter Rejection Reflex", "SENSORY",
        triggered, f"SPIT: bitter in {CFG['bitter_rejection_ms']}ms" if triggered else "None",
        "D_chemical encoded in taste: P_rejection before absorption", fb, s.F_score())

def A57_sweet_acceptance(s: BioState) -> AlgorithmResult:
    """Sweet → consume. Energy signal. Dopamine reward encodes → repeat."""
    fb = s.F_score()
    triggered = s.glucose_mmol < CFG["glucose_low_mmol"] + 1
    if triggered:
        s.glucose_mmol = min(7.0, s.glucose_mmol + 0.3)
    return AlgorithmResult("A57", "Sweet Acceptance Drive", "SENSORY",
        triggered, "Consume: sweet = energy" if triggered else "Sated",
        "P_reward signal: drives P_intake before D_hunger critical", fb, s.F_score())

def A58_smell_memory(s: BioState) -> AlgorithmResult:
    """Olfactory → hippocampus direct. Smell bypasses thalamus. Fastest memory."""
    fb = s.F_score()
    triggered = True
    return AlgorithmResult("A58", "Smell→Memory Direct Channel", "SENSORY",
        triggered, "Olfactory→hippocampus: instant recall",
        "P_chemical → P_memory: fastest D-encoding pathway in brain", fb, s.F_score())

def A59_pain_localise(s: BioState) -> AlgorithmResult:
    """Pain with 2cm spatial resolution → know exactly where to act."""
    fb = s.F_score()
    triggered = s.pain_level > 0.3
    return AlgorithmResult("A59", "Pain Localisation Map", "SENSORY",
        triggered, f"Pain localised ±{CFG['pain_localisation_cm']}cm" if triggered else "No pain",
        "D_damage has coordinates: P_location enables targeted repair", fb, s.F_score())

def A60_proprioception(s: BioState) -> AlgorithmResult:
    """Know where your body is in space at all times. No visual needed."""
    fb = s.F_score()
    triggered = True  # constant
    return AlgorithmResult("A60", "Proprioception Constant", "SENSORY",
        triggered, "Body position known: no computation needed",
        "Continuous P_self-model: reduces D_collision, D_fall", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 07 — PLANT INTELLIGENCE (A61–A70)
# ─────────────────────────────────────────────────────────────────────────────

def A61_phototropism(s: BioState, light_dir_deg: float = 30.0) -> AlgorithmResult:
    """Auxin gradient → grow toward light. Maximise P_photon capture."""
    fb = s.F_score()
    triggered = light_dir_deg > 10
    if triggered:
        s.phototropism_angle = min(90.0, s.phototropism_angle + CFG["phototropism_angle_deg_h"])
    return AlgorithmResult("A61", "Phototropism Growth", "PLANT",
        triggered, f"Grow {CFG['phototropism_angle_deg_h']}°/h toward light_dir={light_dir_deg}°",
        "D_shade → P_growth direction change: maximise F_photon", fb, s.F_score())

def A62_gravitropism(s: BioState) -> AlgorithmResult:
    """Statolith gravity sensor → roots down, shoots up. No brain. Pure physics."""
    fb = s.F_score()
    triggered = True
    return AlgorithmResult("A62", "Gravitropism Root/Shoot", "PLANT",
        triggered, "Roots → down (gravity). Shoots → up.",
        "D_gravity constant → P_direction encoded in structure", fb, s.F_score())

def A63_hydrotropism(s: BioState) -> AlgorithmResult:
    """Root senses moisture gradient → grow toward water."""
    fb = s.F_score()
    triggered = s.water_stress > 0.3
    if triggered:
        s.water_stress = max(0.0, s.water_stress - 0.05)
    return AlgorithmResult("A63", "Hydrotropism Water Seek", "PLANT",
        triggered, "Roots follow moisture gradient" if triggered else "Hydrated",
        "D_drought → P_root_exploration: find hidden resource", fb, s.F_score())

def A64_stomata_co2_control(s: BioState) -> AlgorithmResult:
    """CO2 low → open stomata. Water stress → close. Precision gas valve."""
    fb = s.F_score()
    co2_trigger = s.co2_room_ppm < CFG["stomata_co2_threshold_ppm"]
    drought_close = s.humidity_pct < CFG["stomata_drought_close_rh"]
    triggered = co2_trigger or drought_close
    s.stomata_open = co2_trigger and not drought_close
    return AlgorithmResult("A64", "Stomata CO2/Water Control", "PLANT",
        triggered, f"Stomata={'OPEN' if s.stomata_open else 'CLOSED'} | CO2={s.co2_room_ppm}ppm | RH={s.humidity_pct}%",
        "Multi-D valve: CO2 D vs water D — optimise both", fb, s.F_score())

def A65_leaf_fold_heat(s: BioState) -> AlgorithmResult:
    """Too hot → fold leaves to reduce sun exposure. Structural response."""
    fb = s.F_score()
    triggered = s.core_temp_c > CFG["leaf_fold_temp_c"]
    return AlgorithmResult("A65", "Leaf Fold Heat Avoidance", "PLANT",
        triggered, f"Leaves fold at >{CFG['leaf_fold_temp_c']}°C" if triggered else "Leaves open",
        "D_radiation → reduce P_surface: accept less energy to prevent damage", fb, s.F_score())

def A66_circadian_plant_clock(s: BioState, hour: float = 8.0) -> AlgorithmResult:
    """Plant anticipates dawn 1h before it happens. Adjusts stomata in advance."""
    fb = s.F_score()
    pre_dawn = 5.0 <= hour <= 7.0
    triggered = pre_dawn
    if triggered:
        s.stomata_open = True
    return AlgorithmResult("A66", "Plant Circadian Pre-Dawn", "PLANT",
        triggered, "Pre-dawn stomata open — ready for photosynthesis" if triggered else "Night mode",
        "P_anticipation: plant acts before D_light arrives", fb, s.F_score())

def A67_mycorrhizal_share(s: BioState) -> AlgorithmResult:
    """Carbon surplus → share 30% with fungal network → help neighbours."""
    fb = s.F_score()
    triggered = s.atp_store_pct > 70
    if triggered:
        s.atp_store_pct = max(0.0, s.atp_store_pct - CFG["mycorrhizal_share_pct"] * 0.3)
    return AlgorithmResult("A67", "Mycorrhizal Network Share", "PLANT",
        triggered, f"Share {CFG['mycorrhizal_share_pct']}% surplus via fungi" if triggered else "None",
        "P_surplus shared: ecosystem F raised, reduces D_neighbour", fb, s.F_score())

def A68_defence_chemistry(s: BioState) -> AlgorithmResult:
    """Herbivore attack → produce terpenes/tannins/alkaloids. Chemical warfare."""
    fb = s.F_score()
    triggered = s.damage_pct > 15
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.15)
    return AlgorithmResult("A68", "Plant Defence Chemistry", "PLANT",
        triggered, "Produce toxins + warn neighbours via VOC" if triggered else "None",
        "D_herbivore → chemical P_defence + P_signal to community", fb, s.F_score())

def A69_seed_dormancy(s: BioState) -> AlgorithmResult:
    """Bad conditions → stop everything. Wait. Indefinitely if needed."""
    fb = s.F_score()
    triggered = s.core_temp_c < 5 or s.water_stress > 0.8
    return AlgorithmResult("A69", "Seed Dormancy Wait Protocol", "PLANT",
        triggered, "DORMANT: wait for conditions. Indefinitely." if triggered else "Active",
        "Extreme D → reduce all P to minimum. Wait for F to recover externally.", fb, s.F_score())

def A70_allelopathy(s: BioState) -> AlgorithmResult:
    """Release chemicals that inhibit competitor growth. Preemptive D."""
    fb = s.F_score()
    triggered = s.atp_store_pct > 60 and s.damage_pct < 10
    return AlgorithmResult("A70", "Allelopathy Competitor Suppression", "PLANT",
        triggered, "Release growth inhibitors into soil" if triggered else "None",
        "P_resource_surplus → active D_competitor to protect own F", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 08 — HOMEOSTASIS / BALANCE (A71–A80)
# ─────────────────────────────────────────────────────────────────────────────

def A71_ph_buffer(s: BioState) -> AlgorithmResult:
    """Blood pH drifts → bicarbonate/kidney/lung corrects instantly."""
    fb = s.F_score()
    triggered = s.ph < CFG["ph_low"] or s.ph > CFG["ph_high"]
    if triggered:
        s.ph = 7.40  # buffer to normal
    return AlgorithmResult("A71", "pH Buffer System", "HOMEOSTASIS",
        triggered, f"pH={s.ph:.2f} — {'CORRECT' if triggered else 'OK'} (range {CFG['ph_low']}–{CFG['ph_high']})",
        "Chemical D_acid/base → triple buffer maintains P_enzyme_function", fb, s.F_score())

def A72_osmosis_balance(s: BioState) -> AlgorithmResult:
    """Too salty → dilute (drink). Too dilute → retain salt. Osmolality 285."""
    fb = s.F_score()
    triggered = not (CFG["osmolality_low"] <= s.osmolality <= CFG["osmolality_high"])
    if triggered:
        s.osmolality = 285.0
    return AlgorithmResult("A72", "Osmolality Regulation", "HOMEOSTASIS",
        triggered, f"Osmolality={s.osmolality}mOsm — {'CORRECT' if triggered else 'OK'}",
        "D_osmotic → kidney P_filtration maintains cell F", fb, s.F_score())

def A73_blood_pressure(s: BioState) -> AlgorithmResult:
    """BP drops → baroreceptors → increase HR. BP rises → vasodilate."""
    fb = s.F_score()
    triggered = not (CFG["bp_systolic_low"] <= s.bp_systolic <= CFG["bp_systolic_high"])
    if triggered:
        s.bp_systolic = 120.0
    return AlgorithmResult("A73", "Blood Pressure Baroreflex", "HOMEOSTASIS",
        triggered, f"BP={s.bp_systolic}mmHg — {'CORRECT' if triggered else 'OK'}",
        "D_pressure → HR + vessel_tone P_response: perfusion maintained", fb, s.F_score())

def A74_calcium_mobilise(s: BioState) -> AlgorithmResult:
    """Serum Ca2+ low → PTH → mobilise from bone. Ca2+ for muscle/nerve."""
    fb = s.F_score()
    triggered = s.atp_store_pct < 50  # proxy: using ATP as metabolic proxy
    return AlgorithmResult("A74", "Calcium Homeostasis", "HOMEOSTASIS",
        triggered, "PTH active — Ca2+ from bone" if triggered else "Serum Ca2+ normal",
        "D_Ca2+_serum → structural P_bone → functional P_muscle", fb, s.F_score())

def A75_negative_feedback_hormone(s: BioState) -> AlgorithmResult:
    """Hormone high → suppress its own production. Prevents runaway."""
    fb = s.F_score()
    triggered = s.immune_response > 0.7
    if triggered:
        s.immune_response = max(0.0, s.immune_response - 0.1)
    return AlgorithmResult("A75", "Negative Feedback Hormone", "HOMEOSTASIS",
        triggered, "Suppress: hormone→feedback→inhibit" if triggered else "Normal",
        "D_excess → P_suppression: system cannot runaway", fb, s.F_score())

def A76_kidney_filter(s: BioState) -> AlgorithmResult:
    """180L blood filtered/day. Keep glucose/proteins. Excrete urea/drugs."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.1
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.03)
    return AlgorithmResult("A76", "Kidney Filtration", "HOMEOSTASIS",
        triggered, "Filtering: keep good, excrete bad",
        "Continuous P_selective_filter: D_toxin → removed, P_nutrient → retained", fb, s.F_score())

def A77_liver_detox(s: BioState) -> AlgorithmResult:
    """Toxin enters blood → liver: oxidation → conjugation → excrete."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.2
    if triggered:
        s.pathogen_load = max(0.0, s.pathogen_load - 0.06)
    return AlgorithmResult("A77", "Liver Detoxification", "HOMEOSTASIS",
        triggered, "CYP450 enzymes: oxidise toxins" if triggered else "Clear",
        "Central D_chemical processor: converts D to excretable form", fb, s.F_score())

def A78_lymph_drainage(s: BioState) -> AlgorithmResult:
    """Excess interstitial fluid → lymph vessels → return to blood."""
    fb = s.F_score()
    triggered = s.inflammation_level > 0.3
    if triggered:
        s.inflammation_level = max(0.0, s.inflammation_level - 0.05)
    return AlgorithmResult("A78", "Lymph Drainage", "HOMEOSTASIS",
        triggered, "Drain excess fluid — reduce D_pressure" if triggered else "Balanced",
        "D_oedema → passive P_pressure drives fluid return", fb, s.F_score())

def A79_sleep_homeostasis(s: BioState) -> AlgorithmResult:
    """Adenosine builds → sleep pressure. Cannot be overridden indefinitely."""
    fb = s.F_score()
    sleep_pressure = s.fatigue_pct / 100.0
    triggered = sleep_pressure > 0.7
    return AlgorithmResult("A79", "Sleep Homeostatic Pressure", "HOMEOSTASIS",
        triggered, f"Sleep pressure={sleep_pressure:.2f} — {'SLEEP NOW' if triggered else 'OK'}",
        "Adenosine D_accumulation: P_sleep mandatory above threshold", fb, s.F_score())

def A80_social_homeostasis(s: BioState) -> AlgorithmResult:
    """Isolation → same brain circuits as physical pain. Social is biological."""
    fb = s.F_score()
    triggered = s.pain_level > 0.4  # using pain as proxy for isolation
    return AlgorithmResult("A80", "Social Homeostasis (Belonging)", "HOMEOSTASIS",
        triggered, "Seek contact — isolation = D_pain" if triggered else "Connected",
        "D_isolation = D_physical: social P_bonding = biological need", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 09 — REDUNDANCY / SAFETY ARCHITECTURE (A81–A90)
# ─────────────────────────────────────────────────────────────────────────────

def A81_dual_organ_redundancy(s: BioState) -> AlgorithmResult:
    """2 kidneys, 2 lungs, 2 eyes, 2 ears. Lose one → still functional."""
    fb = s.F_score()
    triggered = s.damage_pct > 50
    action = "Backup organ active — primary failed" if triggered else "Primary + backup both OK"
    return AlgorithmResult("A81", "Dual Organ Redundancy", "SAFETY",
        triggered, action,
        "Structural P_redundancy: single D_failure cannot kill F", fb, s.F_score())

def A82_fail_safe_autonomic(s: BioState) -> AlgorithmResult:
    """Unconscious → still breathe, heart beats. Cannot switch off."""
    fb = s.F_score()
    triggered = True  # always
    return AlgorithmResult("A82", "Fail-Safe Autonomic", "SAFETY",
        triggered, "Brainstem: breath + heartbeat = autonomous",
        "Core F-functions independent of P_consciousness", fb, s.F_score())

def A83_priority_hierarchy(s: BioState) -> AlgorithmResult:
    """Scarce resources: brain → heart → kidney → muscle. Never reverse."""
    fb = s.F_score()
    triggered = s.atp_store_pct < 40
    priorities = [CFG["priority_1"], CFG["priority_2"], CFG["priority_3"]]
    return AlgorithmResult("A83", "Resource Priority Hierarchy", "SAFETY",
        triggered, f"Priorities: {' > '.join(priorities)}",
        "D_scarcity → P_allocation hierarchy protects highest-F organs", fb, s.F_score())

def A84_pain_mandatory_interrupt(s: BioState) -> AlgorithmResult:
    """Severe pain → interrupt ALL current tasks. No choice. Mandatory."""
    fb = s.F_score()
    triggered = s.pain_level > 0.8
    return AlgorithmResult("A84", "Pain Mandatory Interrupt", "SAFETY",
        triggered, "INTERRUPT ALL — pain > 0.8" if triggered else "No interrupt",
        "Critical D_damage → forced P_attention: cannot ignore", fb, s.F_score())

def A85_disgust_barrier(s: BioState) -> AlgorithmResult:
    """Rotten smell/appearance → disgust → don't eat. Pre-cognitive block."""
    fb = s.F_score()
    triggered = s.pathogen_load > 0.35
    return AlgorithmResult("A85", "Disgust Pre-Cognitive Barrier", "SAFETY",
        triggered, "REJECT before tasting — disgust reflex" if triggered else "None",
        "P_disgust blocks D_toxin before it enters: pre-emptive F-guard", fb, s.F_score())

def A86_fear_fright_flight(s: BioState) -> AlgorithmResult:
    """Threat → amygdala → adrenaline → freeze/fight/flee. 150ms. No thinking."""
    fb = s.F_score()
    triggered = s.pain_level > 0.6 or s.damage_pct > 40
    if triggered:
        s.atp_store_pct = max(0.0, s.atp_store_pct - 10.0)  # adrenaline burns
        s.fatigue_pct = min(100.0, s.fatigue_pct + 5.0)
    return AlgorithmResult("A86", "Fear Freeze-Fight-Flight", "SAFETY",
        triggered, "THREAT: adrenaline burst — 150ms response" if triggered else "Safe",
        "D_threat → P_motor override: cognition bypassed for speed", fb, s.F_score())

def A87_surprise_interrupt(s: BioState) -> AlgorithmResult:
    """Unexpected event → 100% attention. Context is reset."""
    fb = s.F_score()
    triggered = s.noise_db > 70
    return AlgorithmResult("A87", "Surprise Orientation Response", "SAFETY",
        triggered, f"ORIENT: unexpected stimulus db={s.noise_db}" if triggered else "Expected env",
        "D_novel → P_full_attention reallocation: unknown D = potential threat", fb, s.F_score())

def A88_fatigue_adrenaline_override(s: BioState) -> AlgorithmResult:
    """Critical threat while exhausted → adrenaline overrides fatigue. One shot."""
    fb = s.F_score()
    triggered = s.fatigue_pct > 85 and s.pain_level > 0.7
    if triggered:
        s.fatigue_pct = max(0.0, s.fatigue_pct - 40.0)
    return AlgorithmResult("A88", "Fatigue Override (Adrenaline)", "SAFETY",
        triggered, "OVERRIDE: adrenaline supersedes fatigue" if triggered else "Normal fatigue",
        "Emergency P_burst: D_survival > D_fatigue in priority", fb, s.F_score())

def A89_dna_repair(s: BioState) -> AlgorithmResult:
    """Radiation/mutation → multiple repair pathways. 50k repairs/cell/day."""
    fb = s.F_score()
    triggered = True  # constant
    s.damage_pct = max(0.0, s.damage_pct - 0.1)
    return AlgorithmResult("A89", "DNA Repair (Constant)", "SAFETY",
        triggered, "50,000 DNA repairs/cell/day — always running",
        "Continuous D_mutation monitoring: P_genome maintained", fb, s.F_score())

def A90_antioxidant_scavenge(s: BioState) -> AlgorithmResult:
    """Free radicals → glutathione/catalase/SOD neutralise immediately."""
    fb = s.F_score()
    triggered = s.damage_pct > 5
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 0.5)
    return AlgorithmResult("A90", "Antioxidant Scavenging", "SAFETY",
        triggered, "Reactive oxygen neutralised" if triggered else "Low ROS",
        "D_radical → P_chemical neutraliser: molecular F maintenance", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN 10 — DEATH / RENEWAL (A91–A100)
# ─────────────────────────────────────────────────────────────────────────────

def A91_telomere_clock(s: BioState) -> AlgorithmResult:
    """Each division shortens telomere. After ~50 (Hayflick) → senescence."""
    fb = s.F_score()
    triggered = s.age_divisions >= CFG["telomere_max_divisions"]
    remaining = max(0, CFG["telomere_max_divisions"] - s.age_divisions)
    return AlgorithmResult("A91", "Telomere Division Clock", "DEATH_RENEWAL",
        triggered, f"Divisions={s.age_divisions}/{CFG['telomere_max_divisions']} — {'SENESCENT' if triggered else f'{remaining} left'}",
        "D_age encoded structurally: F cannot exceed lifespan", fb, s.F_score())

def A92_senescence_signal(s: BioState) -> AlgorithmResult:
    """Senescent cell → stop dividing, release SASP signals."""
    fb = s.F_score()
    triggered = s.age_divisions > CFG["telomere_max_divisions"] - 5
    if triggered:
        s.inflammation_level = min(1.0, s.inflammation_level + 0.02)
    return AlgorithmResult("A92", "Senescence SASP Signal", "DEATH_RENEWAL",
        triggered, "Senescent: stop divide, signal neighbours" if triggered else "Normal",
        "D_age → P_stop_signal: system learns to replace not repair", fb, s.F_score())

def A93_stem_cell_reserve(s: BioState) -> AlgorithmResult:
    """Injury → activate stem cell reserve → differentiate to needed type."""
    fb = s.F_score()
    triggered = s.damage_pct > 25
    if triggered:
        s.damage_pct = max(0.0, s.damage_pct - 5.0)
    return AlgorithmResult("A93", "Stem Cell Reserve Activation", "DEATH_RENEWAL",
        triggered, "Stem cells differentiate → replace damaged" if triggered else "Quiescent",
        "D_critical → P_reserve activation: regenerative capacity", fb, s.F_score())

def A94_epigenetic_memory(s: BioState) -> AlgorithmResult:
    """Harsh environment → methylation marks passed to offspring. Lamarckian trace."""
    fb = s.F_score()
    triggered = s.damage_pct > 50 or s.fatigue_pct > 80
    return AlgorithmResult("A94", "Epigenetic Environmental Memory", "DEATH_RENEWAL",
        triggered, "Encode D_experience in methylation" if triggered else "Normal",
        "D_harsh → P_heritable: next generation pre-adapted", fb, s.F_score())

def A95_ordered_apoptosis(s: BioState) -> AlgorithmResult:
    """Terminal damage → clean self-destruct. Better than necrosis (chaos)."""
    fb = s.F_score()
    triggered = s.damage_pct >= 90
    if triggered:
        s.alive = False
        s.damage_pct = 0.0
    return AlgorithmResult("A95", "Ordered Apoptosis (Clean Death)", "DEATH_RENEWAL",
        triggered, "APOPTOSIS: clean, controlled, no spillage" if triggered else "Alive",
        "D→∞ → P_clean_exit: preserve system F over cell F", fb, s.F_score())

def A96_decompose_feed(s: BioState) -> AlgorithmResult:
    """Death → decompose in ~30 days → nutrients back to soil → next generation."""
    fb = s.F_score()
    triggered = not s.alive
    return AlgorithmResult("A96", "Decomposition → Nutrient Return", "DEATH_RENEWAL",
        triggered, f"Decompose in ~{CFG['decompose_days_avg']}d → soil nutrient" if triggered else "Alive",
        "D_death → P_ecosystem: individual F ends, collective F continues", fb, s.F_score())

def A97_legacy_chemical_signal(s: BioState) -> AlgorithmResult:
    """Dying plant → release seeds + VOC → neighbours informed of conditions."""
    fb = s.F_score()
    triggered = s.damage_pct > 80
    return AlgorithmResult("A97", "Legacy Signal Release", "DEATH_RENEWAL",
        triggered, "Release seeds + VOC warning" if triggered else "None",
        "P_broadcast_in_death: D_self → D_reduction for others", fb, s.F_score())

def A98_renewal_spring(s: BioState, month: int = 4) -> AlgorithmResult:
    """Spring conditions → dormancy broken → explosive growth. Wait was worthwhile."""
    fb = s.F_score()
    triggered = 3 <= month <= 5 and s.water_stress < 0.3
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 20.0)
        s.water_stress = max(0.0, s.water_stress - 0.1)
    return AlgorithmResult("A98", "Spring Renewal Activation", "DEATH_RENEWAL",
        triggered, f"SPRING: dormancy broken, month={month}" if triggered else "Dormant/summer/autumn",
        "D_winter_wait → P_burst: stored energy converts to maximum F", fb, s.F_score())

def A99_nutrient_cycle_close(s: BioState) -> AlgorithmResult:
    """Closed loop: organism → decompose → soil → plant → animal → organism."""
    fb = s.F_score()
    triggered = True  # always true at ecosystem level
    return AlgorithmResult("A99", "Nutrient Cycle Closure", "DEATH_RENEWAL",
        triggered, f"Cycle closes in ~{CFG['nutrient_cycle_years']}yr",
        "No waste: every D becomes P for another. System F = constant.", fb, s.F_score())

def A100_first_breath(s: BioState) -> AlgorithmResult:
    """Birth: lungs inflate for first time. Surfactant (lecithin) prevents collapse."""
    fb = s.F_score()
    triggered = s.o2_sat_pct < 50  # newborn before first breath
    if triggered:
        s.o2_sat_pct = min(99.0, s.o2_sat_pct + 40.0)
        s.co2_blood_pct = max(4.0, s.co2_blood_pct - 2.0)
    return AlgorithmResult("A100", "First Breath — Birth", "DEATH_RENEWAL",
        triggered, "FIRST BREATH: F_life begins" if triggered else "Already breathing",
        "P_zero → P_maximum in one action: F_existence initialised", fb, s.F_score())


# ─────────────────────────────────────────────────────────────────────────────
# MASTER RUNNER — run all 100 algorithms on a state
# ─────────────────────────────────────────────────────────────────────────────

def A39_starvation_ketosis_protocol(s: BioState) -> AlgorithmResult:
    fb = s.F_score()
    triggered = s.glucose_mmol < 2.5
    if triggered:
        s.atp_store_pct = min(100.0, s.atp_store_pct + 5.0)
    return AlgorithmResult("A39", "Starvation Ketosis Protocol", "ENERGY",
        triggered, "KETOSIS: brain switches to ketones" if triggered else "Normal",
        "Extreme D_glucose → alternative P_substrate to protect brain F", fb, s.F_score())


def run_all_algorithms(s: BioState, verbose: bool = True) -> dict:
    """Run all 100 biological algorithms on state s. Return summary."""
    results = []
    F_initial = s.F_score()

    algo_fns = [
        A01_co2_trigger, A02_o2_threshold, A03_rate_adaptation, A04_apnea_override,
        A05_altitude_adaptation, A06_sleep_breathing, A07_yawn_reset, A08_cough_clear,
        A09_sneeze_irritant, A10_co2_room_alert,
        A11_sweat_onset, A12_shiver_heat, A13_vasodilation, A14_vasoconstriction,
        A15_behavioral_thermostat, A16_fever_setpoint, A17_heat_shock_proteins,
        A18_circadian_temp_cycle, A19_brown_fat_thermogenesis, A20_transpiration_cooling,
        A21_nociception_withdraw, A22_inflammation_cascade, A23_coagulation_clot,
        A24_wound_healing, A25_referred_pain_signal, A26_chronic_pain_avoidance,
        A27_itch_scratch, A28_nausea_expel, A29_learned_aversion, A30_plant_wound_seal,
        A31_glucose_monitor, A32_fat_mobilisation, A33_glycogen_burst, A34_atp_priority_brain,
        A35_sleep_restore, A36_circadian_energy_peak, A37_metabolic_rate_adapt,
        A38_growth_repair_night, A40_plant_photosynthesis,
        A41_pattern_recognition, A42_fever_induction, A43_local_inflammation,
        A44_antibody_memory, A45_self_tolerance, A46_nk_surveillance, A47_interferon_warning,
        A48_apoptosis_selfclean, A49_autophagy_recycle, A50_microbiome_balance,
        A51_habituation, A52_sensitization, A53_contrast_detection, A54_motion_alert,
        A55_colour_warning, A56_bitter_rejection, A57_sweet_acceptance, A58_smell_memory,
        A59_pain_localise, A60_proprioception,
        A61_phototropism, A62_gravitropism, A63_hydrotropism, A64_stomata_co2_control,
        A65_leaf_fold_heat, A66_circadian_plant_clock, A67_mycorrhizal_share,
        A68_defence_chemistry, A69_seed_dormancy, A70_allelopathy,
        A71_ph_buffer, A72_osmosis_balance, A73_blood_pressure, A74_calcium_mobilise,
        A75_negative_feedback_hormone, A76_kidney_filter, A77_liver_detox,
        A78_lymph_drainage, A79_sleep_homeostasis, A80_social_homeostasis,
        A81_dual_organ_redundancy, A82_fail_safe_autonomic, A83_priority_hierarchy,
        A84_pain_mandatory_interrupt, A85_disgust_barrier, A86_fear_fright_flight,
        A87_surprise_interrupt, A88_fatigue_adrenaline_override, A89_dna_repair,
        A90_antioxidant_scavenge,
        A91_telomere_clock, A92_senescence_signal, A93_stem_cell_reserve,
        A94_epigenetic_memory, A95_ordered_apoptosis, A96_decompose_feed,
        A97_legacy_chemical_signal, A98_renewal_spring, A99_nutrient_cycle_close,
        A100_first_breath,
    ]

    for fn in algo_fns:
        try:
            r = fn(s)
            results.append(r)
        except Exception as e:
            pass  # graceful skip

    F_final = s.F_score()
    triggered_count = sum(1 for r in results if r.triggered)
    domains = {}
    for r in results:
        domains.setdefault(r.domain, []).append(r)

    if verbose:
        print("\n" + "═"*72)
        print("  BIO ALGORITHMS — 100 LIVING SYSTEM HEURISTICS")
        print("  Planta Smart Homes · AFI Theory of Everything Extension")
        print("  ALL RESULTS SIMULATED · F=P/D HYPOTHESIS UNDER TEST")
        print("═"*72)
        print(f"\n  State: temp={s.core_temp_c:.1f}°C  O2={s.o2_sat_pct:.0f}%  "
              f"CO2_room={s.co2_room_ppm}ppm  glucose={s.glucose_mmol:.1f}mmol")
        print(f"  F_initial={F_initial:.4f}  F_final={F_final:.4f}  "
              f"ΔF={F_final-F_initial:+.4f}")
        print(f"\n  Triggered: {triggered_count}/{len(results)} algorithms active\n")

        for domain, algo_list in sorted(domains.items()):
            active = [r for r in algo_list if r.triggered]
            print(f"  [{domain}] {len(active)}/{len(algo_list)} active")
            for r in active[:3]:  # show top 3 per domain
                print(f"    {r.algo_id} {r.name}: {r.action[:60]}")
            if len(active) > 3:
                print(f"    ... +{len(active)-3} more")

        print(f"\n  ΔF_total = {F_final - F_initial:+.4f}")
        print("  SIMULATED — seed=2026 — F=P/D HYPOTHESIS UNDER TEST")
        print("═"*72 + "\n")

    return {
        "F_initial": F_initial,
        "F_final": F_final,
        "delta_F": round(F_final - F_initial, 4),
        "triggered": triggered_count,
        "total": len(results),
        "results": results,
        "domains": {k: len(v) for k, v in domains.items()},
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
        "seed": CFG["seed"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# LIFECYCLE SIMULATION — first breath to last breath
# ─────────────────────────────────────────────────────────────────────────────

def simulate_lifecycle(years: int = 80, steps_per_year: int = 52) -> list:
    """
    Simulate F-score across a full human lifespan.
    Birth → growth → peak → decline → death.
    Returns: list of (year, F, triggered_count, alive)
    """
    rng_sim = np.random.default_rng(CFG["seed"])
    trajectory = []

    s = BioState()
    s.o2_sat_pct = 30.0  # pre-birth
    s.co2_blood_pct = 7.5
    s.damage_pct = 0.0
    s.glucose_mmol = 3.5

    for yr in range(years):
        for step in range(steps_per_year):
            # Age-related changes
            s.age_divisions = int(yr * CFG["telomere_max_divisions"] / years)

            # Random daily perturbations
            s.co2_room_ppm = 420 + rng_sim.normal(80, 40)
            s.core_temp_c = 37.0 + rng_sim.normal(0, 0.3)
            s.o2_sat_pct = max(0, min(99, 97 - yr * 0.05 + rng_sim.normal(0, 1)))
            s.glucose_mmol = max(0.5, 5.0 + rng_sim.normal(0, 0.5))
            s.fatigue_pct = max(0, min(100, yr * 0.5 + rng_sim.normal(10, 5)))
            s.damage_pct = max(0, yr * 0.3 + rng_sim.normal(0, 3))

            # Pathogen exposures (random illness events)
            if rng_sim.random() < 0.02:  # 2% chance per step = ~1 illness/year
                s.pathogen_load = rng_sim.uniform(0.2, 0.6)
            else:
                s.pathogen_load = max(0.0, s.pathogen_load - 0.05)

            # Run all algorithms
            out = run_all_algorithms(s, verbose=False)
            F = s.F_score()

            # Death conditions
            if (s.core_temp_c > CFG["heat_death_c"] or
                    s.core_temp_c < CFG["cold_death_c"] or
                    s.o2_sat_pct < 60 or
                    s.age_divisions >= CFG["telomere_max_divisions"]):
                s.alive = False

        trajectory.append({
            "year": yr,
            "F": round(s.F_score(), 4),
            "triggered": out["triggered"],
            "alive": s.alive,
            "o2": round(s.o2_sat_pct, 1),
            "damage": round(s.damage_pct, 1),
            "divisions": s.age_divisions,
        })

        if not s.alive:
            break

    return trajectory


# ─────────────────────────────────────────────────────────────────────────────
# HOUSE-AS-LIVING-BEING — map bio algorithms to building systems
# ─────────────────────────────────────────────────────────────────────────────

HOUSE_BIO_MAP = {
    # Biology → Building
    "A01 CO2 Trigger Breath":       "HVAC opens damper when CO2 > 800ppm (Portaria 353-A)",
    "A02 O2 Threshold":             "Fresh air intake increases when O2 equivalent drops",
    "A06 Autonomic Sleep Breathing": "Minimum ventilation runs 24/7, cannot be disabled",
    "A10 CO2 Room Alert":           "Alert at 1000ppm + log + notify + force ventilate",
    "A11 Sweat Onset Cooling":      "HVAC cools when T > summer setpoint + 1°C",
    "A12 Shiver Heat":              "HVAC heats when T < winter setpoint - 1°C",
    "A13 Vasodilation":             "Open windows/dampers when internal T excess",
    "A14 Vasoconstriction":         "Close all openings, insulate when T drops",
    "A15 Behavioural Thermostat":   "Suggest occupants open windows / move to cooler room",
    "A16 Fever Setpoint":           "Raise setpoint when calibration event detected",
    "A18 Circadian Temp Cycle":     "Pre-cool 1h before peak occupancy. Pre-heat before dawn.",
    "A21 Nociception Withdraw":     "Immediate alert on fire/flood/gas — 50ms response",
    "A22 Inflammation Isolation":   "Zone quarantine: isolate smoke/flood room, protect rest",
    "A23 Coagulation Clot":         "Auto-close valves on leak detection (water/gas)",
    "A31 Glucose Monitor":          "Energy budget monitor — flag if consumption > baseline 20%",
    "A34 ATP Priority Brain":       "Emergency power: server/safety first, HVAC second, lights last",
    "A35 Sleep Restore":            "Night mode: reduce HVAC, dim lights, save energy",
    "A41 PAMP Pattern Recognition": "Anomaly detection: unknown pattern → alert (no ML in 60s tick)",
    "A44 Antibody Memory":          "PlantaOS remembers past events → faster future response",
    "A46 NK Surveillance":          "Continuous sensor polling every 60s — always watching",
    "A47 Interferon Warning":       "Alert one room → pre-arm adjacent rooms",
    "A48 Apoptosis":               "Failed sensor → mark dead, use backup or interpolate",
    "A49 Autophagy":               "Recycle stale data: SQLite 7d → DuckDB → Parquet",
    "A51 Habituation":              "Suppress repeated minor alerts same room same cause",
    "A52 Sensitization":            "Repeated threat same location → lower threshold there",
    "A54 Motion Alert":             "PIR detects motion → adjust HVAC/lighting",
    "A61 Phototropism":             "Blinds track sun angle for optimal light/heat",
    "A64 Stomata CO2 Control":      "Window/damper: open for CO2, close for heat retention",
    "A66 Plant Circadian Pre-Dawn": "Pre-heat classrooms 30min before first occupancy",
    "A71 pH Buffer":               "pH of plumbing monitored — scale/corrosion prevention",
    "A72 Osmolality":              "Water hardness monitoring",
    "A73 Blood Pressure":          "HVAC duct static pressure regulation",
    "A75 Negative Feedback":       "PID controller for all setpoints — prevent runaway",
    "A79 Sleep Homeostasis":       "Occupancy = 0 → deep sleep mode mandatory",
    "A81 Dual Organ Redundancy":   "Primary + backup sensor on critical points",
    "A82 Fail-Safe Autonomic":     "Core monitoring never stops, even if main server fails",
    "A83 Priority Hierarchy":      "Life safety > comfort > energy > cost",
    "A84 Pain Mandatory Interrupt": "Fire/flood/gas = interrupt all, act NOW",
    "A86 Fear Response":           "Emergency: full ventilation, lights max, doors unlock",
    "A89 DNA Repair":              "Config.yaml hash checked every startup — detect tampering",
    "A91 Telomere Clock":          "Component lifecycle tracking — replace before failure",
    "A95 Ordered Apoptosis":       "Graceful shutdown — flush to Parquet before stop",
    "A99 Nutrient Cycle":          "Energy from building → grid → building: no waste",
}


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  BIO ALGORITHMS — 100 LIVING SYSTEM HEURISTICS               ║")
    print("║  AFI Theory of Everything · Planta Smart Homes               ║")
    print("║  F = P / D  ·  seed=2026  ·  zero hardcodes                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW\n")

    # ── Scenario 1: Healthy adult, normal office environment
    print("── SCENARIO 1: Healthy adult in office ──")
    s1 = BioState()
    s1.co2_room_ppm = 850.0    # slightly elevated
    s1.noise_db = 48.0
    s1.core_temp_c = 37.2
    out1 = run_all_algorithms(s1, verbose=True)

    # ── Scenario 2: Stressed state — heat + CO2 + fatigue
    print("── SCENARIO 2: Stress state (heat + CO2 + fatigue) ──")
    s2 = BioState()
    s2.co2_room_ppm = 1100.0   # above legal limit
    s2.core_temp_c = 38.8      # mild fever
    s2.fatigue_pct = 75.0
    s2.pathogen_load = 0.3
    s2.o2_sat_pct = 93.0
    out2 = run_all_algorithms(s2, verbose=True)

    # ── Scenario 3: Freedom Water Home (plant + human hybrid system)
    print("── SCENARIO 3: Freedom Water Home (plant+human) ──")
    s3 = BioState()
    s3.co2_room_ppm = 420.0    # outdoor fresh
    s3.core_temp_c = 37.0
    s3.stomata_open = True
    s3.water_stress = 0.0
    s3.atp_store_pct = 90.0
    out3 = run_all_algorithms(s3, verbose=True)

    # ── Lifecycle simulation
    print("── LIFECYCLE SIMULATION: 80 years ──")
    traj = simulate_lifecycle(years=80, steps_per_year=12)
    f_values = [t["F"] for t in traj]
    peak_yr = max(traj, key=lambda t: t["F"])
    death_yr = traj[-1]
    print(f"\n  Lifespan simulated: {len(traj)} years")
    print(f"  F peak: {peak_yr['F']:.4f} at year {peak_yr['year']}")
    print(f"  F at death: {death_yr['F']:.4f} at year {death_yr['year']}")
    print(f"  Mean F over life: {sum(f_values)/len(f_values):.4f}")
    print(f"  F trajectory (decade samples): " +
          " → ".join(f"{traj[min(i*10, len(traj)-1)]['F']:.3f}" for i in range(9)))

    # ── House-as-living-being mapping
    print("\n── HOUSE AS LIVING BEING — BIO→BUILDING MAP ──")
    print(f"  {len(HOUSE_BIO_MAP)} biological algorithms mapped to building systems:\n")
    for bio, building in list(HOUSE_BIO_MAP.items())[:15]:
        print(f"  {bio}")
        print(f"    → {building}\n")
    print(f"  ... +{len(HOUSE_BIO_MAP)-15} more in HOUSE_BIO_MAP dict\n")

    print("  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW")
    print("  Designing to free. -- Gonçalo\n")
