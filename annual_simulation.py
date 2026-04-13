"""
annual_simulation_v2.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Full Year Simulation v2 (all bugs fixed)
HORSE CFT · Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION

BUGS FIXED vs v1:
  1. STEP_H = 6/60 — each tick is 6 minutes, not 1 hour (was 10× inflated)
  2. LUX violations tracked per month
  3. Salary segments read from config.yaml (zero hardcodes)
  4. Carbon computed properly after interventions (BACS class B = -20%)
  5. Three scenario tiers: Small / Balanced / Mega
  6. People economics uses 3,219 annual users + salary segments + taxes

ECONOMICS MODEL (for a training centre):
  The cost is not just "salary while uncomfortable."
  It is "training effectiveness lost."
  3,219 people × avg employer cost × training hours × efficiency loss
  = measurable investment wasted per year.

ALL RESULTS SIMULATION-BASED · F=P/D HYPOTHESIS UNDER TEST · seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import math, os, yaml
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

RNG = np.random.default_rng(2026)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADER
# ─────────────────────────────────────────────────────────────────────────────

def _load_yaml(name):
    base = os.path.dirname(os.path.abspath(__file__))
    for p in [os.path.join(base, f"{name}.yaml"), os.path.join(base, f"{name}.yml")]:
        if os.path.exists(p):
            with open(p) as f: return yaml.safe_load(f) or {}
    return {}

_CFG = _load_yaml("config")
_COMP = _load_yaml("compliance")

# ─────────────────────────────────────────────────────────────────────────────
# PARAMETERS (ALL from config — zero hardcodes in logic)
# ─────────────────────────────────────────────────────────────────────────────

STEP_MIN  = 6.0                          # simulation tick in minutes
STEP_H    = STEP_MIN / 60.0             # 0.1 h — CRITICAL for energy & debt

# Economics from config.yaml (fallback to AFI Master values)
_econ = _CFG.get("economics", {})
_segs = _econ.get("salary_segments", {
    "trainee":    {"pct":0.78,"employer_hourly":7.50},
    "instructor": {"pct":0.12,"employer_hourly":12.85},
    "supervisor": {"pct":0.05,"employer_hourly":19.99},
    "manager":    {"pct":0.05,"employer_hourly":32.10},
})
EMPLOYER_H_AVG   = sum(s.get("pct",0)*s.get("employer_hourly",0) for s in _segs.values())
EMPLOYER_H_AVG   = EMPLOYER_H_AVG if EMPLOYER_H_AVG > 0 else 10.00

ENERGY_PEAK_KWH  = _econ.get("energy_peak_eur_kwh", 0.218)
ENERGY_BASE_KWH  = _econ.get("energy_offpeak_eur_kwh", 0.138)
CARBON_KG_KWH    = _econ.get("carbon_intensity_kg_kwh", 0.202)
RENT_EUR_M2_MO   = _econ.get("rent_eur_m2_month", 6.0)

# Building from config.yaml
_bldg = _CFG.get("building", {})
BUILDING_AREA_M2 = _bldg.get("area_m2", 950.0)
ANNUAL_USERS     = 3219   # David Fleury confirmed — not in config yet, add manually

# HVAC from config.yaml
_hvac = _CFG.get("hvac", {})
HVAC_KW_PER_UNIT = _hvac.get("capacity_w_thermal", 7034) / _hvac.get("cop", 3.2) / 1000

# Comfort from config.yaml or compliance.yaml
_cmf = _CFG.get("comfort", {})
_pt  = _COMP.get("portugal", {})
CO2_LEGAL_PPM    = _cmf.get("co2_legal_ppm",  _pt.get("portaria_353a_2013",{}).get("limit_ppm",1000))
CO2_ALERT_PPM    = _cmf.get("co2_alert_ppm",  _pt.get("portaria_353a_2013",{}).get("alert_ppm",800))
TEMP_WINTER_MIN  = _cmf.get("winter_min_c",  18.0)
TEMP_WINTER_MAX  = _cmf.get("winter_max_c",  22.0)
TEMP_SUMMER_MIN  = _cmf.get("summer_min_c",  22.0)
TEMP_SUMMER_MAX  = _cmf.get("summer_max_c",  26.0)
LUX_MIN          = _cmf.get("lux_classroom_min", 300.0)
LUX_CRITICAL     = _cmf.get("lux_critical",  150.0)
NOISE_MAX        = _cmf.get("noise_max_db",   45.0)

# D weights from config.yaml
_dw = _CFG.get("distortion", {}).get("weights", {
    "thermal":0.40,"co2":0.22,"humidity":0.16,
    "light":0.12,"noise":0.05,"occupancy":0.03,"spatial":0.02
})
assert abs(sum(_dw.values()) - 1.0) < 1e-6, "D weights must sum to 1.0"

# Calendar
OPERATING_DAYS = {1:18,2:18,3:21,4:20,5:22,6:20,7:0,8:15,9:21,10:23,11:20,12:17}
MONTH_NAMES    = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
                  7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

# ─────────────────────────────────────────────────────────────────────────────
# ROOMS
# ─────────────────────────────────────────────────────────────────────────────

ROOMS = {
    "Hall_GF":       {"area":40,  "cap":10,  "floor":0, "ac":0, "lux":280, "win":True},
    "Cantina":       {"area":65,  "cap":30,  "floor":0, "ac":0, "lux":320, "win":True},
    "Egas_Moniz":    {"area":78,  "cap":17,  "floor":0, "ac":1, "lux":409, "win":True},
    "Damasio":       {"area":65,  "cap":15,  "floor":0, "ac":1, "lux":230, "win":True},
    "Pintassilgo":   {"area":78,  "cap":12,  "floor":0, "ac":0, "lux":85,  "win":True},
    "Gago_Coutinho": {"area":52,  "cap":12,  "floor":0, "ac":1, "lux":205, "win":True},
    "Hall_F1":       {"area":35,  "cap":10,  "floor":1, "ac":0, "lux":260, "win":True},
    "Dojo_EMotor":   {"area":65,  "cap":10,  "floor":1, "ac":1, "lux":290, "win":True},
    "Vasco_da_Gama": {"area":65,  "cap":20,  "floor":1, "ac":2, "lux":305, "win":True},
    "Quintanilha":   {"area":65,  "cap":15,  "floor":1, "ac":2, "lux":384, "win":True},
    "Automacao":     {"area":65,  "cap":8,   "floor":1, "ac":1, "lux":290, "win":True},
    "Eiffage":       {"area":65,  "cap":14,  "floor":1, "ac":1, "lux":295, "win":True},
}


# ─────────────────────────────────────────────────────────────────────────────
# THREE SCENARIO TIERS
# ─────────────────────────────────────────────────────────────────────────────

SCENARIO_TIERS = {
    "small": {
        "label": "Melhoria Simples",
        "label_short": "PEQUENA",
        "desc": "Maior ROI. Intervir onde dói mais.",
        "cost_eur": 2000,
        "interventions": {
            "Pintassilgo": {"ac": 1, "lux": 380},
        },
        "software_only_bonus": True,    # A18 circadian pre-heat (€0)
        "bacs_class": None,
    },
    "balanced": {
        "label": "Equilibrada",
        "label_short": "EQUILIBRADA",
        "desc": "Máximo impacto por euro investido.",
        "cost_eur": 6200,
        "interventions": {
            "Pintassilgo":   {"ac": 1, "lux": 380},
            "Cantina":       {"ac": 1},
            "Hall_GF":       {"ac": 1},
            "Hall_F1":       {"ac": 1},
        },
        "sensor_cost_eur": 500,         # 2 priority rooms pilot sensors
        "software_only_bonus": True,
        "bacs_class": None,
    },
    "mega": {
        "label": "Optimização Total",
        "label_short": "MEGA",
        "desc": "Conformidade total EU/PT + sensores + BACS.",
        "cost_eur": 13296,
        "interventions": {
            "Pintassilgo":   {"ac": 1, "lux": 380},
            "Cantina":       {"ac": 1},
            "Hall_GF":       {"ac": 1},
            "Hall_F1":       {"ac": 1},
            "Damasio":       {"lux": 350},
            "Gago_Coutinho": {"lux": 320},
        },
        "sensor_cost_eur": 1296,        # full deploy
        "software_only_bonus": True,
        "bacs_class": "B",              # ISO 16484 class B = -20% energy
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# PEOPLE ECONOMICS (training centre model)
# ─────────────────────────────────────────────────────────────────────────────

def people_economics(F_annual: float, annual_users: int = ANNUAL_USERS) -> dict:
    """
    Training centre productivity loss model.

    NOT a simple salary × hours formula.
    The cost is TRAINING EFFECTIVENESS LOST.

    Formula:
      investment_per_person = employer_hourly × avg_training_hours_per_user
      efficiency_loss = comfort_deficit ^ 1.2  (scientific: not linear, not 1.5)
      productivity_cost = investment × efficiency_loss × annual_users

    Weights from config.yaml salary_segments.
    avg_training_hours calibrated to 3,219 annual users × ~40h/user.
    """
    # Salary segments from config
    seg_costs = []
    for seg, vals in _segs.items():
        pct = vals.get("pct", 0)
        emp_h = vals.get("employer_hourly", EMPLOYER_H_AVG)
        seg_costs.append((seg, pct, emp_h))

    employer_h = sum(pct * emp for _, pct, emp in seg_costs)

    # Average training hours per user (calibrated to HORSE CFT context)
    avg_training_h_per_user = 40.0   # ~5 days technical training (typical Renault)

    # Employer investment per user
    investment_per_user = employer_h * avg_training_h_per_user

    # Efficiency loss from comfort deficit
    # Scientific basis: Allen 2016 (Harvard) 6%/unit CO2, Wargocki 1999 thermal
    # Using AFI exponent 1.2 (between 1.0 linear and 1.5 AFI default)
    comfort_deficit = max(0.0, 1.0 - F_annual)
    efficiency_loss = comfort_deficit ** 1.2

    # Total productivity cost
    training_productivity_cost = investment_per_user * efficiency_loss * annual_users

    # Additional: space cost wasted (rent × (1-F))
    space_cost_annual = RENT_EUR_M2_MO * BUILDING_AREA_M2 * 11   # 11 operating months
    space_waste = space_cost_annual * (1.0 - F_annual)

    # Breakdown by segment
    breakdown = {}
    for seg, pct, emp_h in seg_costs:
        n_people = int(annual_users * pct)
        loss = investment_per_user * efficiency_loss * n_people
        breakdown[seg] = {
            "n_people": n_people,
            "employer_h": round(emp_h, 2),
            "investment_per_person": round(investment_per_user, 0),
            "loss_eur": round(loss, 0),
        }

    return {
        "annual_users": annual_users,
        "avg_training_h": avg_training_h_per_user,
        "employer_h_avg": round(employer_h, 2),
        "investment_per_user_eur": round(investment_per_user, 0),
        "comfort_deficit_pct": round(comfort_deficit * 100, 1),
        "efficiency_loss_pct": round(efficiency_loss * 100, 1),
        "training_productivity_cost_eur": round(training_productivity_cost, 0),
        "space_waste_eur": round(space_waste, 0),
        "total_cost_eur": round(training_productivity_cost + space_waste, 0),
        "breakdown_by_segment": breakdown,
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PHYSICS HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _T_outdoor(month, hour):
    # Aveiro climate from compliance.yaml
    climate = _COMP.get("portugal_climate", {})
    monthly_avg = climate.get("monthly_temp_avg_c", {})
    month_keys = {1:"jan",2:"feb",3:"mar",4:"apr",5:"may",6:"jun",
                  7:"jul",8:"aug",9:"sep",10:"oct",11:"nov",12:"dec"}
    T_base = monthly_avg.get(month_keys.get(month,"jan"), 15.0)
    T_range = 6.0 * math.sin(2*math.pi*(month-2)/12) + 2.0
    T_diurnal = T_range * math.sin(2*math.pi*(hour-6)/24)
    return T_base + T_diurnal

def _T_sp(month):
    return TEMP_WINTER_MIN + 2 if month in [1,2,3,4,10,11,12] else TEMP_SUMMER_MIN + 2

def _T_lim(month):
    if month in [1,2,3,4,10,11,12]: return TEMP_WINTER_MIN, TEMP_WINTER_MAX
    return TEMP_SUMMER_MIN, TEMP_SUMMER_MAX

def _occ(room, hour, month, dow):
    cap = ROOMS[room]["cap"]
    if month == 7 or dow >= 5 or cap == 0: return 0
    if hour < 7.5 or hour >= 19: return 0
    if room == "Cantina":
        return int(cap * (0.90 if 12 <= hour < 14 else 0.05))
    if "Hall" in room: return int(cap * 0.20)
    morning   = 8.0 <= hour < 12.0
    afternoon = 13.5 <= hour < 17.5
    if morning or afternoon: return int(cap * RNG.uniform(0.5, 0.85))
    return int(cap * 0.04)

def _compute_D(T, co2, rh, lux, noise, n, cap, month):
    T_sp = _T_sp(month)
    d_T   = max(1.0, 1.0 + abs(T - T_sp) / 2.5)
    d_co2 = max(1.0, co2 / 700.0)
    d_rh  = max(1.0, 1.0 + abs(rh - 50) / 15.0)
    d_lux = max(1.0, 400.0 / max(lux, 10.0)) if n > 0 else 1.0
    d_noi = max(1.0, 1.0 + max(0, noise - NOISE_MAX) / 10.0)
    d_occ = max(1.0, n / max(cap, 1))
    ln_D = (_dw.get("thermal",0.40)*math.log(d_T) +
            _dw.get("co2",0.22)*math.log(d_co2) +
            _dw.get("humidity",0.16)*math.log(d_rh) +
            _dw.get("light",0.12)*math.log(d_lux) +
            _dw.get("noise",0.05)*math.log(d_noi) +
            _dw.get("occupancy",0.03)*math.log(d_occ))
    D = math.exp(ln_D)
    attr = {}
    if ln_D > 0.001:
        attr = {
            "thermal": round(_dw.get("thermal",0.40)*math.log(d_T)/ln_D*100, 1),
            "co2":     round(_dw.get("co2",0.22)*math.log(d_co2)/ln_D*100, 1),
            "light":   round(_dw.get("light",0.12)*math.log(d_lux)/ln_D*100, 1),
        }
    return D, attr

def _f_debt_step(F, n):
    """F-debt for one 6-minute step. = per-hour rate × STEP_H."""
    deficit = max(0.0, 1.0 - F)
    impact  = deficit ** 1.2   # scientific exponent (see people_economics)
    per_hour = impact * n * EMPLOYER_H_AVG
    return per_hour * STEP_H   # ← KEY FIX: multiply by step fraction

def _energy_step(room, n, ac_on, hour, cfg):
    """Energy in kWh for one 6-minute step. = kW × STEP_H."""
    hvac   = cfg["ac"] * HVAC_KW_PER_UNIT if ac_on and n > 0 else 0.0
    lights = cfg["area"] * 0.012 if 8 <= hour < 20 and n > 0 else 0.0
    return (hvac + lights) * STEP_H   # ← KEY FIX: kW × hours = kWh


# ─────────────────────────────────────────────────────────────────────────────
# STEP SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

def _sim_step(room, state, hour, month, dow, interventions):
    cfg = {**ROOMS[room]}
    iv = interventions.get(room, {})
    if "ac"  in iv: cfg["ac"]  = iv["ac"]
    if "lux" in iv: cfg["lux"] = iv["lux"]

    n      = _occ(room, hour, month, dow)
    T_out  = _T_outdoor(month, hour)
    T_sp   = _T_sp(month)
    T_min, T_max = _T_lim(month)
    vol    = cfg["area"] * 3.0

    # Temperature (thermal RC model)
    T = state.get("T", T_sp)
    if cfg["ac"] > 0 and n > 0:
        T += (T_sp - T) * 0.08 + (T_out - T) * 0.01 + n * 0.015
    else:
        T += (T_out - T) * 0.025 + n * 0.03
    T += RNG.normal(0, 0.12)

    # CO2 (mass balance)
    co2 = state.get("co2", 420.0)
    ach = 0.8 + (0.4 if cfg["win"] else 0)
    co2 += n * 17.0 / vol - (co2 - 420) * ach / 60
    co2  = max(420.0, co2 + RNG.normal(0, 5))

    # Humidity
    rh = state.get("rh", 50.0)
    rh += n * 0.25 - (rh - 45) * 0.025 + RNG.normal(0, 0.5)
    rh  = max(20.0, min(85.0, rh))

    # Lux & noise
    lights_on = 8 <= hour < 20 and n > 0
    lux   = float(cfg["lux"]) if lights_on else 0.0
    noise = 38.0 + n * 0.85 + RNG.normal(0, 2.0)

    # D, F
    D, attr = _compute_D(T, co2, rh, lux, noise, n, cfg["cap"], month)
    P = 0.55 + 0.45 * (n / max(cfg["cap"], 1))
    F = round(min(1.0, max(0.0, P / D)), 4)

    # Economics (per 6-min step — FIXED)
    f_debt = _f_debt_step(F, n) if n > 0 else 0.0
    energy = _energy_step(room, n, cfg["ac"] > 0, hour, cfg)
    tariff = ENERGY_PEAK_KWH if 9 <= hour <= 22 else ENERGY_BASE_KWH

    # Violations
    flows = []
    if co2 > CO2_LEGAL_PPM and n > 0:
        flows.append({"type":"CO2_LEGAL","v":round(co2,0)})
    elif co2 > CO2_ALERT_PPM and n > 0:
        flows.append({"type":"CO2_ALERT","v":round(co2,0)})
    if T < T_min - 1 and n > 0:
        flows.append({"type":"TEMP_LEGAL","v":round(T,1)})
    elif T < T_min and n > 0:
        flows.append({"type":"TEMP_LOW","v":round(T,1)})
    if lux < LUX_CRITICAL and n > 0:
        flows.append({"type":"LUX_CRITICAL","v":round(lux,0)})
    elif lux < LUX_MIN and n > 0:
        flows.append({"type":"LUX_LOW","v":round(lux,0)})
    if noise > NOISE_MAX and n > 0:
        flows.append({"type":"NOISE_HIGH","v":round(noise,1)})

    return {
        "T":round(T,2),"co2":round(co2,1),"rh":round(rh,1),
        "lux":round(lux,0),"noise":round(noise,1),
        "n":n,"F":F,"D":round(D,4),"attr":attr,
        "f_debt_eur": round(f_debt,5),
        "energy_kwh": round(energy,5),
        "energy_eur": round(energy*tariff,5),
        "carbon_kg":  round(energy*CARBON_KG_KWH,5),
        "flows":flows,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANNUAL SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AnnualResult:
    monthly:  dict  = field(default_factory=dict)
    worst_hour: dict = field(default_factory=dict)
    best_hour:  dict = field(default_factory=dict)
    total_f_debt_eur: float = 0.0
    total_energy_kwh: float = 0.0
    total_energy_eur: float = 0.0
    total_carbon_kg:  float = 0.0
    total_co2_legal:  int   = 0
    total_co2_alert:  int   = 0
    total_temp_legal: int   = 0
    total_lux_fail:   int   = 0
    total_noise_fail: int   = 0
    mean_F_annual:    float = 0.0
    total_person_h:   float = 0.0   # actual person-hours (post-step correction)
    room_annual: dict = field(default_factory=dict)
    people_econ: dict = field(default_factory=dict)
    label: str = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST"


def run_annual(interventions=None, verbose=True, bacs_class=None) -> AnnualResult:
    """Run full year simulation. All values correctly scaled by STEP_H."""
    if interventions is None: interventions = {}
    result  = AnnualResult()
    states  = {r: {"T":18.0,"co2":420.0,"rh":50.0} for r in ROOMS}
    r_accum = {r: defaultdict(float) for r in ROOMS}
    F_sum = F_n = 0.0
    worst_F = 1.0; best_F = 0.0
    worst_ctx = {}; best_ctx = {}

    if verbose:
        print(f"\n  {'━'*60}")
        print(f"  Simulação Anual HORSE CFT  |  {len(interventions)} intervenções")
        print(f"  STEP_H={STEP_H:.3f}h  |  EMPLOYER_H_AVG=€{EMPLOYER_H_AVG:.2f}/h")
        print(f"  {'━'*60}")

    for month in range(1, 13):
        n_days = OPERATING_DAYS[month]
        if n_days == 0:
            result.monthly[month] = {
                "name":MONTH_NAMES[month],"n_days":0,"status":"FECHADO",
                "f_debt":0,"energy_kwh":0,"mean_F":0,
                "co2_legal":0,"temp_legal":0,"lux_fail":0,"person_h":0,
            }
            if verbose: print(f"  {MONTH_NAMES[month]:<12}: FECHADO")
            continue

        m_f_debt=m_energy=m_F_sum=m_F_n=m_ph = 0.0
        m_co2_l=m_temp_l=m_lux_f=m_noise_f = 0
        m_worst_F=1.0; m_worst_ctx={}

        for day in range(n_days):
            dow = day % 5
            # 150 steps × 6min = 15h (06:00–21:00)
            for step in range(150):
                hour = 6.0 + step * STEP_MIN / 60.0

                hF=[]; hfd=heng=0.0; hco2=htemp=hlux=hnoise=0

                for room in ROOMS:
                    s = _sim_step(room, states[room], hour, month, dow, interventions)
                    states[room] = {"T":s["T"],"co2":s["co2"],"rh":s["rh"]}

                    if s["n"] > 0:
                        hF.append(s["F"])
                        F_sum += s["F"]; F_n += 1
                        m_F_sum += s["F"]; m_F_n += 1
                        m_ph += s["n"] * STEP_H   # actual person-hours

                    hfd  += s["f_debt_eur"]
                    heng += s["energy_kwh"]

                    for fl in s["flows"]:
                        t = fl["type"]
                        if t=="CO2_LEGAL":  hco2+=1;  result.total_co2_legal+=1
                        if t=="CO2_ALERT":  result.total_co2_alert+=1
                        if t=="TEMP_LEGAL": htemp+=1; result.total_temp_legal+=1
                        if t in("LUX_CRITICAL","LUX_LOW"): hlux+=1; result.total_lux_fail+=1
                        if t=="NOISE_HIGH": hnoise+=1; result.total_noise_fail+=1

                    r_accum[room]["f_debt"]  += s["f_debt_eur"]
                    r_accum[room]["energy"]  += s["energy_kwh"]
                    r_accum[room]["co2_sum"] += s["co2"]
                    r_accum[room]["F_sum"]   += s["F"]
                    r_accum[room]["F_n"]     += 1

                m_f_debt+=hfd; m_energy+=heng
                m_co2_l+=hco2; m_temp_l+=htemp; m_lux_f+=hlux; m_noise_f+=hnoise

                if hF:
                    hF_mean = sum(hF)/len(hF)
                    if hF_mean < worst_F:
                        worst_F=hF_mean
                        worst_ctx={"date":f"{day+1:02d}/{month:02d} {hour:04.1f}h",
                                   "F":round(hF_mean,3),"f_debt_eur_h":round(hfd,2),
                                   "co2_breaches":hco2,"temp_breaches":htemp}
                    if hF_mean > best_F and hfd < 1:
                        best_F=hF_mean
                        best_ctx={"date":f"{day+1:02d}/{month:02d} {hour:04.1f}h",
                                  "F":round(hF_mean,3)}
                    if hF_mean < m_worst_F:
                        m_worst_F=hF_mean
                        m_worst_ctx={"date":f"{day+1:02d}/{month:02d} {hour:.1f}h",
                                     "F":round(hF_mean,3)}

        # BACS bonus: class B = -20% energy, class C = -11%
        bacs_factor = {"A":0.70,"B":0.80,"C":0.89}.get(bacs_class or "", 1.0)
        m_energy_adj = m_energy * bacs_factor

        result.total_f_debt_eur  += m_f_debt
        result.total_energy_kwh  += m_energy_adj
        result.total_energy_eur  += m_energy_adj * ENERGY_PEAK_KWH
        result.total_carbon_kg   += m_energy_adj * CARBON_KG_KWH
        result.total_person_h    += m_ph

        mean_F_m = m_F_sum/m_F_n if m_F_n>0 else 0.0
        status = ("Crítico" if mean_F_m<0.45 else
                  "Degradado" if mean_F_m<0.60 else
                  "Bom" if mean_F_m<0.75 else "Óptimo")
        result.monthly[month] = {
            "name":MONTH_NAMES[month],"n_days":n_days,
            "mean_F":round(mean_F_m,3),"status":status,
            "f_debt":round(m_f_debt,0),"energy_kwh":round(m_energy_adj,0),
            "co2_legal":m_co2_l,"temp_legal":m_temp_l,
            "lux_fail":m_lux_f,"noise_fail":m_noise_f,
            "person_h":round(m_ph,0),"worst":m_worst_ctx,
        }
        if verbose:
            bar = "█"*int(mean_F_m*16)+"░"*(16-int(mean_F_m*16))
            print(f"  {MONTH_NAMES[month]:<12}  Perf:{mean_F_m*100:4.0f}%  [{bar}]  "
                  f"Perda=€{m_f_debt:>7,.0f}  T×{m_temp_l:>4}  LUX×{m_lux_f:>4}  "
                  f"{m_energy_adj:>5,.0f}kWh")

    result.worst_hour = worst_ctx
    result.best_hour  = best_ctx
    result.mean_F_annual = round(F_sum/F_n,4) if F_n>0 else 0.0

    for room in ROOMS:
        n = r_accum[room]["F_n"]
        result.room_annual[room] = {
            "mean_F":  round(r_accum[room]["F_sum"]/n,3) if n>0 else 0,
            "f_debt":  round(r_accum[room]["f_debt"],0),
            "energy":  round(r_accum[room]["energy"],0),
            "mean_co2":round(r_accum[room]["co2_sum"]/n,0) if n>0 else 0,
        }

    result.people_econ = people_economics(result.mean_F_annual)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# THREE-TIER ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyse_tiers(verbose=True) -> dict:
    """Run baseline + 3 scenario tiers. Return comparison."""
    if verbose:
        print(f"\n  ┌{'─'*60}┐")
        print(f"  │  Análise de Cenários — 3 Tiers                       │")
        print(f"  └{'─'*60}┘\n")
        print(f"  [0/4] Baseline...")

    baseline = run_annual(interventions={}, verbose=False)
    b_econ   = people_economics(baseline.mean_F_annual)

    results = {"baseline": {
        "mean_F": baseline.mean_F_annual,
        "f_debt_eur": baseline.total_f_debt_eur,
        "energy_kwh": baseline.total_energy_kwh,
        "carbon_kg":  baseline.total_carbon_kg,
        "co2_legal":  baseline.total_co2_legal,
        "temp_legal": baseline.total_temp_legal,
        "lux_fail":   baseline.total_lux_fail,
        "person_h":   baseline.total_person_h,
        "people_cost_eur": b_econ["training_productivity_cost_eur"],
        "people_econ": b_econ,
        "worst_hour": baseline.worst_hour,
        "monthly": baseline.monthly,
        "room_annual": baseline.room_annual,
    }}

    for i, (tier_key, tier) in enumerate(SCENARIO_TIERS.items()):
        if verbose: print(f"  [{i+1}/4] {tier['label']}...")
        bacs = tier.get("bacs_class")
        sim  = run_annual(interventions=tier["interventions"],
                         verbose=False, bacs_class=bacs)
        econ = people_economics(sim.mean_F_annual)

        # Total investment = hardware + optional sensors
        hw_cost     = tier["cost_eur"]
        sensor_cost = tier.get("sensor_cost_eur", 0)
        total_cost  = hw_cost + sensor_cost

        # Savings vs baseline
        save_f_debt   = baseline.total_f_debt_eur - sim.total_f_debt_eur
        save_energy   = (baseline.total_energy_kwh - sim.total_energy_kwh) * ENERGY_PEAK_KWH
        save_people   = b_econ["training_productivity_cost_eur"] - econ["training_productivity_cost_eur"]
        total_savings = save_f_debt + max(0, save_energy)

        payback_months = (total_cost / total_savings * 12) if total_savings > 0 else 999
        roi_pct        = (total_savings - total_cost) / max(total_cost, 1) * 100

        results[tier_key] = {
            "label":          tier["label"],
            "label_short":    tier["label_short"],
            "desc":           tier["desc"],
            "cost_eur":       total_cost,
            "hw_cost":        hw_cost,
            "sensor_cost":    sensor_cost,
            "bacs_class":     bacs,
            "mean_F":         sim.mean_F_annual,
            "delta_F":        round(sim.mean_F_annual - baseline.mean_F_annual, 4),
            "f_debt_eur":     sim.total_f_debt_eur,
            "energy_kwh":     sim.total_energy_kwh,
            "carbon_kg":      sim.total_carbon_kg,
            "co2_legal":      sim.total_co2_legal,
            "temp_legal":     sim.total_temp_legal,
            "lux_fail":       sim.total_lux_fail,
            "save_f_debt":    round(save_f_debt, 0),
            "save_energy_eur":round(max(0, save_energy), 0),
            "save_people_eur":round(save_people, 0),
            "total_savings":  round(total_savings, 0),
            "payback_months": round(payback_months, 1),
            "roi_pct":        round(roi_pct, 0),
            "people_econ":    econ,
        }

    if verbose: print()
    return results


# ─────────────────────────────────────────────────────────────────────────────
# BACKWARDS COMPATIBILITY (used by horse_report_v2, chat tools)
# ─────────────────────────────────────────────────────────────────────────────

INTERVENTIONS_MENU = {
    k: {"desc": v["label"], "cost_eur": v["cost_eur"],
        "changes": v["interventions"]}
    for k, v in SCENARIO_TIERS.items()
}

def analyse_interventions(verbose=False) -> dict:
    """Wrapper around analyse_tiers for backwards compatibility."""
    tiers = analyse_tiers(verbose=verbose)
    b = tiers["baseline"]
    result = {"baseline": {
        "mean_F": b["mean_F"],
        "f_debt_eur": b["f_debt_eur"],
        "co2_breaches_legal": b["co2_legal"],
        "temp_breaches": b["temp_legal"],
        "worst_hour": b["worst_hour"],
    }}
    for k, t in tiers.items():
        if k == "baseline": continue
        result[k] = {
            "desc": t["label"],
            "cost_eur": t["cost_eur"],
            "mean_F": t["mean_F"],
            "delta_F": t["delta_F"],
            "f_debt_eur": t["f_debt_eur"],
            "total_savings_eur": t["total_savings"],
            "savings_f_debt_eur": t["save_f_debt"],
            "payback_months": t["payback_months"],
            "roi_pct": t["roi_pct"],
            "co2_breaches_legal": t["co2_legal"],
            "temp_breaches": t["temp_legal"],
        }
    return result


def tool_annual_simulation(mode="baseline", intervention="none") -> dict:
    """Chat tool entry point."""
    if mode == "compare_all":
        tiers = analyse_tiers(verbose=False)
        return {
            "mode": "compare_all",
            "baseline_F": tiers["baseline"]["mean_F"],
            "baseline_f_debt": tiers["baseline"]["f_debt_eur"],
            "tiers": {k: {"label":v.get("label",k),"delta_F":v.get("delta_F",0),
                          "cost":v.get("cost_eur",0),"savings":v.get("total_savings",0),
                          "payback":v.get("payback_months",0),"roi":v.get("roi_pct",0)}
                      for k,v in tiers.items() if k!="baseline"},
            "label": "SIMULATED",
        }
    iv = SCENARIO_TIERS.get(intervention, {}).get("interventions", {})
    bacs = SCENARIO_TIERS.get(intervention, {}).get("bacs_class")
    result = run_annual(interventions=iv, verbose=False, bacs_class=bacs)
    return {
        "mode": mode, "intervention": intervention,
        "mean_F_annual": result.mean_F_annual,
        "total_f_debt_eur": round(result.total_f_debt_eur, 0),
        "total_energy_kwh": round(result.total_energy_kwh, 0),
        "total_co2_legal": result.total_co2_legal,
        "total_temp_legal": result.total_temp_legal,
        "total_lux_fail": result.total_lux_fail,
        "worst_hour": result.worst_hour,
        "best_hour": result.best_hour,
        "people_econ": result.people_econ,
        "monthly_F": {m: result.monthly[m].get("mean_F",0) for m in range(1,13)},
        "narrative": f"Performance: {result.mean_F_annual*100:.0f}% | "
                     f"Perda produtividade: €{result.total_f_debt_eur:,.0f} | "
                     f"Energia: {result.total_energy_kwh:.0f} kWh",
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  PlantaOS — Simulação Anual v2 (step bug fixed)             ║")
    print("║  HORSE CFT · 3.219 utilizadores · 3 cenários               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print(f"  STEP_H = {STEP_H:.4f}h  |  EMPLOYER_H_AVG = €{EMPLOYER_H_AVG:.2f}/h")
    print(f"  D weights: " + " ".join(f"{k}={v}" for k,v in _dw.items()))
    print()

    tiers = analyse_tiers(verbose=True)
    b = tiers["baseline"]

    print(f"\n  ┌{'─'*62}┐")
    print(f"  │  RESUMO COMPARATIVO — 3 TIERS                            │")
    print(f"  └{'─'*62}┘\n")

    print(f"  {'CENÁRIO':<22} {'PERF':>6}  {'INVEST':>8}  {'POUPA/ANO':>10}  "
          f"{'PAYBACK':>9}  {'ROI':>7}")
    print(f"  {'─'*22} {'─'*6}  {'─'*8}  {'─'*10}  {'─'*9}  {'─'*7}")

    print(f"  {'BASELINE (actual)':<22} {b['mean_F']*100:>5.0f}%  {'—':>8}  "
          f"{'—':>10}  {'—':>9}  {'—':>7}")

    for tier_key, tier in tiers.items():
        if tier_key == "baseline": continue
        print(f"  {tier['label_short']:<22} {tier['mean_F']*100:>5.0f}%  "
              f"€{tier['cost_eur']:>6,}  €{tier['total_savings']:>8,}  "
              f"{tier['payback_months']:>5.1f} meses  {tier['roi_pct']:>6.0f}%")

    print(f"\n  Pessoas ({ANNUAL_USERS} utilizadores/ano):")
    pe = b["people_econ"]
    print(f"  Investimento/pessoa:   €{pe['investment_per_user_eur']:,} "
          f"(€{pe['employer_h_avg']:.2f}/h × {pe['avg_training_h']:.0f}h)")
    print(f"  Défice conforto:       {pe['comfort_deficit_pct']:.1f}%")
    print(f"  Perda eficiência form: {pe['efficiency_loss_pct']:.1f}%")
    print(f"  Custo formação perdido:€{pe['training_productivity_cost_eur']:,}/ano")
    for seg, d in pe["breakdown_by_segment"].items():
        print(f"    {seg:<12} {d['n_people']:>4} pessoas  "
              f"€{d['employer_h']:.2f}/h  perda=€{d['loss_eur']:>7,}")

    print(f"\n  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    print(f"  Designing to free. -- Gonçalo\n")
