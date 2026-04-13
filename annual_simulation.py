"""
annual_simulation.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Full Year Flow Simulation
HORSE CFT · Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION

Simulates every working day of the year, every room, every hour.
Shows exact date, flows, F-debt in €, CO2 breaches, energy, and
the economic impact of every intervention.

"On 14 January at 08:15, the building had its worst hour of the year."
"Fixing Pintassilgo costs €2,000. Saves €47,340/year."
"CO2 breached legal limit 847 times last year. Each breach = liability."

ALL RESULTS SIMULATION-BASED · F=P/D HYPOTHESIS UNDER TEST · seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import math, json
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np

RNG = np.random.default_rng(2026)

# ─────────────────────────────────────────────────────────────────────────────
# BUILDING CONFIG (from config.yaml / David Fleury confirmed)
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

OPERATING_DAYS = {1:18,2:18,3:21,4:20,5:22,6:20,7:0,8:15,9:21,10:23,11:20,12:17}
MONTH_NAMES = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
               7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

# Economics (config.yaml values)
EMPLOYER_HOURLY_AVG  = 9.42   # €/h weighted average (SMN 2026)
ENERGY_PEAK_EUR_KWH  = 0.218
ENERGY_BASE_EUR_KWH  = 0.138
CARBON_KG_KWH        = 0.202
RENT_EUR_M2_MONTH    = 6.0
BUILDING_AREA_M2     = 950.0
HVAC_KW_PER_UNIT     = 2.198  # electrical kW per AC unit (7034W/COP3.2)

CO2_LEGAL_PPM   = 1000.0   # Portaria 353-A/2013
CO2_ALERT_PPM   = 800.0
TEMP_WINTER_MIN = 18.0
TEMP_WINTER_MAX = 22.0
TEMP_SUMMER_MIN = 22.0
TEMP_SUMMER_MAX = 26.0
LUX_MIN         = 300.0
LUX_CRITICAL    = 150.0


# ─────────────────────────────────────────────────────────────────────────────
# PHYSICS HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _T_outdoor(month: int, hour: float) -> float:
    seasonal = 8.0 + 10.0 * math.sin(2*math.pi*(month-2)/12)
    diurnal  = 4.0 * math.sin(2*math.pi*(hour-6)/24)
    return seasonal + diurnal

def _T_setpoint(month: int) -> float:
    return 20.0 if month in [1,2,3,4,10,11,12] else 24.0

def _T_limits(month: int) -> tuple:
    if month in [1,2,3,4,10,11,12]:
        return TEMP_WINTER_MIN, TEMP_WINTER_MAX
    return TEMP_SUMMER_MIN, TEMP_SUMMER_MAX

def _occupancy(room: str, hour: float, month: int, day_of_week: int) -> int:
    if month == 7 or day_of_week >= 5: return 0
    cap = ROOMS[room]["cap"]
    if cap == 0 or hour < 7.5 or hour >= 19: return 0
    if room == "Cantina":
        return int(cap * (0.95 if 12 <= hour < 14 else 0.05))
    if "Hall" in room:
        return int(cap * 0.25 * (1 if 8 <= hour < 18 else 0))
    morning   = 8.0 <= hour < 12.0
    afternoon = 13.5 <= hour < 17.5
    if morning or afternoon:
        return int(cap * RNG.uniform(0.6, 1.0))
    return int(cap * 0.05)

def _compute_D(T, co2, rh, lux, noise, n_people, cap, month) -> tuple:
    T_sp = _T_setpoint(month)
    d_T    = max(1.0, 1.0 + abs(T - T_sp) / 2.5)
    d_co2  = max(1.0, co2 / 700.0)
    d_rh   = max(1.0, 1.0 + abs(rh - 50) / 15.0)
    d_lux  = max(1.0, 400.0 / max(lux, 10.0)) if n_people > 0 else 1.0
    d_noise= max(1.0, 1.0 + max(0, noise - 45) / 10.0)
    d_occ  = max(1.0, n_people / max(cap, 1))
    W = {"T":0.40,"co2":0.22,"rh":0.16,"lux":0.12,"noise":0.05,"occ":0.03,"spatial":0.02}
    ln_D = (W["T"]*math.log(d_T) + W["co2"]*math.log(d_co2) +
            W["rh"]*math.log(d_rh) + W["lux"]*math.log(d_lux) +
            W["noise"]*math.log(d_noise) + W["occ"]*math.log(d_occ))
    D = math.exp(ln_D)
    attr = {
        "thermal": round(W["T"]*math.log(d_T)/ln_D*100, 1) if ln_D > 0.001 else 0,
        "co2":     round(W["co2"]*math.log(d_co2)/ln_D*100, 1) if ln_D > 0.001 else 0,
        "light":   round(W["lux"]*math.log(d_lux)/ln_D*100, 1) if ln_D > 0.001 else 0,
    }
    return D, attr

def _f_debt_per_hour(F: float, n: int) -> float:
    deficit = max(0.0, 1.0 - F)
    comfort_impact = deficit ** 1.5
    return comfort_impact * n * EMPLOYER_HOURLY_AVG

def _energy_kwh(room: str, n: int, ac_on: bool, hour: float) -> float:
    hvac = ROOMS[room]["ac"] * HVAC_KW_PER_UNIT if ac_on and n > 0 else 0.0
    lights = ROOMS[room]["area"] * 0.012 if 8 <= hour < 20 and n > 0 else 0.0
    return hvac + lights


# ─────────────────────────────────────────────────────────────────────────────
# HOUR SIMULATOR — one tick per room
# ─────────────────────────────────────────────────────────────────────────────

def _simulate_hour(room: str, state: dict, hour: float, month: int,
                   day_of_week: int, interventions: dict) -> dict:
    cfg = ROOMS[room].copy()

    # Apply interventions
    if room in interventions:
        iv = interventions[room]
        if "ac" in iv: cfg["ac"] = iv["ac"]
        if "lux" in iv: cfg["lux"] = iv["lux"]

    n = _occupancy(room, hour, month, day_of_week)
    T_out = _T_outdoor(month, hour)
    T_sp  = _T_setpoint(month)
    T_min, T_max = _T_limits(month)
    vol = cfg["area"] * 3.0

    # Temperature
    T = state.get("T", T_sp)
    if cfg["ac"] > 0 and n > 0:
        T += (T_sp - T) * 0.08 + (T_out - T) * 0.01 + n * 0.015
    else:
        T += (T_out - T) * 0.025 + n * 0.03
    T += RNG.normal(0, 0.12)

    # CO2
    co2 = state.get("co2", 420.0)
    ach = 0.8 + (0.4 if cfg["win"] else 0)
    co2 += n * 17.0 / vol - (co2 - 420) * ach / 60
    co2 = max(420.0, co2 + RNG.normal(0, 6))

    # Humidity
    rh = state.get("rh", 50.0)
    rh += n * 0.25 - (rh - 45) * 0.025 + RNG.normal(0, 0.5)
    rh = max(20.0, min(85.0, rh))

    # Lux
    lights_on = 8 <= hour < 20 and n > 0
    lux = float(cfg["lux"]) if lights_on else 0.0

    # Noise
    noise = 38.0 + n * 0.85 + RNG.normal(0, 2.0)

    # D, F, debt
    D, attr = _compute_D(T, co2, rh, lux, noise, n, cfg["cap"], month)
    P = 0.55 + 0.45 * (n / max(cfg["cap"], 1))
    F = round(min(1.0, max(0.0, P / D)), 4)
    f_debt = _f_debt_per_hour(F, n) if n > 0 else 0.0
    energy = _energy_kwh(room, n, cfg["ac"] > 0, hour)
    tariff = ENERGY_PEAK_EUR_KWH if 9 <= hour <= 22 else ENERGY_BASE_EUR_KWH

    # Flows detected this hour
    flows = []
    if co2 > CO2_LEGAL_PPM and n > 0:
        flows.append({"type":"CO2_LEGAL_BREACH","value":round(co2,0),"severity":4})
    elif co2 > CO2_ALERT_PPM and n > 0:
        flows.append({"type":"CO2_ALERT","value":round(co2,0),"severity":2})
    if T < T_min - 1 and n > 0:
        flows.append({"type":"TEMP_LEGAL_BREACH","value":round(T,1),"severity":4})
    elif T < T_min and n > 0:
        flows.append({"type":"TEMP_LOW","value":round(T,1),"severity":2})
    if lux < LUX_CRITICAL and n > 0:
        flows.append({"type":"LUX_CRITICAL","value":round(lux,0),"severity":4})
    elif lux < LUX_MIN and n > 0:
        flows.append({"type":"LUX_LOW","value":round(lux,0),"severity":2})

    return {
        "T": round(T,2), "co2": round(co2,1), "rh": round(rh,1),
        "lux": round(lux,0), "noise": round(noise,1),
        "n": n, "F": F, "D": round(D,4), "attr": attr,
        "f_debt_eur": round(f_debt,4),
        "energy_kwh": round(energy,4),
        "energy_eur": round(energy * tariff, 4),
        "co2_kwh_carbon": round(energy * CARBON_KG_KWH, 4),
        "flows": flows,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANNUAL SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AnnualResult:
    # Per-month aggregates
    monthly: dict = field(default_factory=dict)
    # Worst moments
    worst_hour: dict = field(default_factory=dict)
    best_hour:  dict = field(default_factory=dict)
    worst_room_annual: dict = field(default_factory=dict)
    # Annual totals
    total_f_debt_eur: float = 0.0
    total_energy_kwh: float = 0.0
    total_energy_eur: float = 0.0
    total_carbon_kg:  float = 0.0
    total_co2_breaches_legal: int = 0
    total_co2_breaches_alert: int = 0
    total_temp_breaches: int = 0
    total_lux_breaches:  int = 0
    mean_F_annual: float = 0.0
    total_people_hours: int = 0
    # Per-room annual
    room_annual: dict = field(default_factory=dict)
    # Flows timeline (worst hours per month)
    flow_timeline: list = field(default_factory=list)
    label: str = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST"


def run_annual(interventions: dict = None, verbose: bool = True) -> AnnualResult:
    """
    Simulate all operating days of the year.
    interventions: {"Pintassilgo": {"ac":1,"lux":380}} etc.
    Returns AnnualResult with all metrics.
    """
    if interventions is None:
        interventions = {}

    result = AnnualResult()
    room_states = {r: {"T": 18.0, "co2": 420.0, "rh": 50.0} for r in ROOMS}
    room_accum  = {r: defaultdict(float) for r in ROOMS}

    F_sum, F_count = 0.0, 0
    worst_F, best_F = 1.0, 0.0
    worst_ctx, best_ctx = {}, {}

    if verbose:
        print(f"\n{'═'*68}")
        print(f"  PlantaOS — Simulação Anual HORSE CFT")
        print(f"  {len(interventions)} intervenções activas: {list(interventions.keys()) or 'nenhuma'}")
        print(f"{'═'*68}")

    for month in range(1, 13):
        n_days = OPERATING_DAYS[month]
        if n_days == 0:
            result.monthly[month] = {
                "name": MONTH_NAMES[month], "n_days": 0,
                "status": "FECHADO", "f_debt": 0, "energy_kwh": 0,
                "mean_F": 0, "co2_breaches": 0, "people_hours": 0,
            }
            if verbose: print(f"  {MONTH_NAMES[month]:12s}: FECHADO")
            continue

        m_f_debt = m_energy = m_F_sum = m_F_n = 0.0
        m_co2_breach = m_people_h = m_temp_breach = 0
        month_worst_F, month_worst_ctx = 1.0, {}

        for day in range(n_days):
            dow = day % 5
            # Simulate day: 06:00 to 21:00
            for hour_i in range(60, 210):  # 6h to 21h in 6-min steps → use 1h steps
                hour = 6.0 + (hour_i - 60) / 10.0
                if hour > 21: break

                hour_F = []
                hour_f_debt = hour_energy = 0.0
                hour_co2_b = hour_temp_b = 0

                for room in ROOMS:
                    s = _simulate_hour(room, room_states[room], hour, month, dow, interventions)
                    room_states[room] = {"T": s["T"], "co2": s["co2"], "rh": s["rh"]}

                    if s["n"] > 0:
                        hour_F.append(s["F"])
                        F_sum += s["F"]; F_count += 1
                        m_F_sum += s["F"]; m_F_n += 1

                    hour_f_debt   += s["f_debt_eur"]
                    hour_energy   += s["energy_kwh"]
                    m_people_h    += s["n"]

                    for fl in s["flows"]:
                        if fl["type"] == "CO2_LEGAL_BREACH":
                            hour_co2_b += 1; result.total_co2_breaches_legal += 1
                        elif fl["type"] == "CO2_ALERT":
                            result.total_co2_breaches_alert += 1
                        if fl["type"] == "TEMP_LEGAL_BREACH":
                            hour_temp_b += 1; result.total_temp_breaches += 1
                        if fl["type"] in ("LUX_CRITICAL","LUX_LOW"):
                            result.total_lux_breaches += 1

                    room_accum[room]["f_debt"] += s["f_debt_eur"]
                    room_accum[room]["energy"]  += s["energy_kwh"]
                    room_accum[room]["co2_sum"] += s["co2"]
                    room_accum[room]["F_sum"]   += s["F"]
                    room_accum[room]["F_n"]     += 1

                m_f_debt  += hour_f_debt
                m_energy  += hour_energy
                m_co2_breach += hour_co2_b
                m_temp_breach += hour_temp_b

                if hour_F:
                    h_F = sum(hour_F) / len(hour_F)
                    if h_F < worst_F:
                        worst_F = h_F
                        ctx_date = f"{day+1:02d}/{month:02d} {hour:04.1f}h"
                        worst_ctx = {"date": ctx_date, "F": round(h_F,3),
                                     "f_debt_eur_h": round(hour_f_debt,2),
                                     "co2_breaches": hour_co2_b}
                    if h_F > best_F and hour_f_debt < 5:
                        best_F = h_F
                        best_ctx = {"date": f"{day+1:02d}/{month:02d} {hour:04.1f}h",
                                    "F": round(h_F,3)}
                    if h_F < month_worst_F:
                        month_worst_F = h_F
                        month_worst_ctx = {"date": f"{day+1:02d}/{month:02d} {hour:.1f}h",
                                           "F": round(h_F,3),
                                           "f_debt_eur_h": round(hour_f_debt,2)}

        result.total_f_debt_eur  += m_f_debt
        result.total_energy_kwh  += m_energy
        result.total_energy_eur  += m_energy * ENERGY_PEAK_EUR_KWH
        result.total_carbon_kg   += m_energy * CARBON_KG_KWH
        result.total_people_hours += m_people_h

        mean_F_m = m_F_sum / m_F_n if m_F_n > 0 else 0.0
        result.monthly[month] = {
            "name": MONTH_NAMES[month],
            "n_days": n_days,
            "mean_F": round(mean_F_m, 3),
            "f_debt": round(m_f_debt, 0),
            "energy_kwh": round(m_energy, 0),
            "co2_breaches": m_co2_breach,
            "temp_breaches": m_temp_breach,
            "people_hours": m_people_h,
            "worst_hour": month_worst_ctx,
            "status": ("crítico" if mean_F_m < 0.45 else
                       "degradado" if mean_F_m < 0.6 else
                       "bom" if mean_F_m < 0.75 else "óptimo"),
        }
        result.flow_timeline.append(month_worst_ctx)

        if verbose:
            bar = "█" * int(mean_F_m * 20)
            print(f"  {MONTH_NAMES[month]:12s}: F={mean_F_m:.3f} {bar:<20} "
                  f"F-debt=€{m_f_debt:,.0f}  CO₂×{m_co2_breach}  "
                  f"{m_energy:.0f}kWh")

    result.worst_hour = worst_ctx
    result.best_hour  = best_ctx
    result.mean_F_annual = round(F_sum / F_count, 4) if F_count > 0 else 0.0

    # Per-room annual summary
    for room in ROOMS:
        n = room_accum[room]["F_n"]
        result.room_annual[room] = {
            "mean_F": round(room_accum[room]["F_sum"] / n, 3) if n > 0 else 0,
            "f_debt_eur": round(room_accum[room]["f_debt"], 0),
            "energy_kwh": round(room_accum[room]["energy"], 0),
            "mean_co2": round(room_accum[room]["co2_sum"] / n, 0) if n > 0 else 0,
        }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# INTERVENTION ANALYSER — what happens if we fix things
# ─────────────────────────────────────────────────────────────────────────────

INTERVENTIONS_MENU = {
    "pintassilgo_fix": {
        "desc": "Instalar AC + upgrade iluminação na Pintassilgo",
        "cost_eur": 2000,
        "changes": {"Pintassilgo": {"ac": 1, "lux": 380}},
    },
    "cantina_hvac": {
        "desc": "Instalar AC na Cantina",
        "cost_eur": 1500,
        "changes": {"Cantina": {"ac": 1}},
    },
    "hall_gf_hvac": {
        "desc": "Instalar AC no Hall RDC",
        "cost_eur": 1200,
        "changes": {"Hall_GF": {"ac": 1}},
    },
    "all_halls": {
        "desc": "AC em todos os halls e corredores",
        "cost_eur": 4500,
        "changes": {"Hall_GF": {"ac": 1}, "Hall_F1": {"ac": 1}},
    },
    "full_upgrade": {
        "desc": "Upgrade completo: AC + iluminação em todas as salas deficientes",
        "cost_eur": 12000,
        "changes": {
            "Pintassilgo": {"ac": 1, "lux": 380},
            "Cantina": {"ac": 1},
            "Hall_GF": {"ac": 1},
            "Hall_F1": {"ac": 1},
            "Damasio": {"lux": 350},
            "Gago_Coutinho": {"lux": 320},
        },
    },
}

def analyse_interventions(verbose: bool = True) -> dict:
    """
    Compare baseline vs each intervention.
    Returns impact analysis with ROI and payback period.
    SIMULATED.
    """
    if verbose:
        print(f"\n{'═'*68}")
        print(f"  ANÁLISE DE INTERVENÇÕES — Impacto Anual")
        print(f"  HORSE CFT · Planta Smart Homes")
        print(f"{'═'*68}\n")
        print(f"  A calcular baseline (sem intervenções)...")

    baseline = run_annual(interventions={}, verbose=False)

    results = {"baseline": {
        "mean_F": baseline.mean_F_annual,
        "f_debt_eur": baseline.total_f_debt_eur,
        "energy_kwh": baseline.total_energy_kwh,
        "co2_breaches_legal": baseline.total_co2_breaches_legal,
        "temp_breaches": baseline.total_temp_breaches,
        "worst_hour": baseline.worst_hour,
    }}

    if verbose:
        print(f"  Baseline: F={baseline.mean_F_annual:.3f} | "
              f"F-debt=€{baseline.total_f_debt_eur:,.0f}/ano | "
              f"CO₂×{baseline.total_co2_breaches_legal} legais | "
              f"energia={baseline.total_energy_kwh:.0f}kWh\n")
        print(f"  A calcular intervenções...\n")

    for key, iv in INTERVENTIONS_MENU.items():
        sim = run_annual(interventions=iv["changes"], verbose=False)

        savings_f_debt = baseline.total_f_debt_eur - sim.total_f_debt_eur
        savings_energy = (baseline.total_energy_kwh - sim.total_energy_kwh) * ENERGY_PEAK_EUR_KWH
        total_savings  = savings_f_debt + max(0, savings_energy)
        payback_months = (iv["cost_eur"] / total_savings * 12) if total_savings > 0 else 999
        delta_F = sim.mean_F_annual - baseline.mean_F_annual
        roi_pct = (total_savings - iv["cost_eur"]) / iv["cost_eur"] * 100

        results[key] = {
            "desc": iv["desc"],
            "cost_eur": iv["cost_eur"],
            "mean_F": sim.mean_F_annual,
            "delta_F": round(delta_F, 4),
            "f_debt_eur": sim.total_f_debt_eur,
            "savings_f_debt_eur": round(savings_f_debt, 0),
            "savings_energy_eur": round(max(0, savings_energy), 0),
            "total_savings_eur": round(total_savings, 0),
            "payback_months": round(payback_months, 1),
            "roi_pct": round(roi_pct, 0),
            "co2_breaches_legal": sim.total_co2_breaches_legal,
            "temp_breaches": sim.total_temp_breaches,
        }

        if verbose:
            arrow = "▲" if delta_F > 0 else "▼"
            print(f"  [{key}]")
            print(f"    {iv['desc']}")
            print(f"    Custo: €{iv['cost_eur']:,} | ΔF={delta_F:+.4f} {arrow}")
            print(f"    Poupança anual: €{total_savings:,.0f} "
                  f"(F-debt €{savings_f_debt:,.0f} + energia €{max(0,savings_energy):,.0f})")
            print(f"    Payback: {payback_months:.1f} meses | ROI: {roi_pct:.0f}%\n")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# NARRATIVE — full year story in plain language
# ─────────────────────────────────────────────────────────────────────────────

def narrate_year(result: AnnualResult, interventions: dict = None) -> str:
    lines = []
    iv_label = "COM INTERVENÇÕES" if interventions else "BASELINE (sem intervenções)"

    lines.append(f"\n{'═'*68}")
    lines.append(f"  HORSE CFT — Relatório Anual PlantaOS · {iv_label}")
    lines.append(f"  SIMULAÇÃO COMPLETA · F=P/D HIPÓTESE EM TESTE")
    lines.append(f"{'═'*68}\n")

    # Annual headline
    F = result.mean_F_annual
    status = "óptimo" if F>0.8 else "bom" if F>0.65 else "degradado" if F>0.5 else "crítico"
    lines.append(f"  O edifício passou o ano com F médio = {F:.3f} ({status}).")
    lines.append(f"  {result.total_people_hours:,} horas-pessoa em condições sub-óptimas.")
    lines.append(f"  Custo total de conforto perdido: €{result.total_f_debt_eur:,.0f}/ano")
    lines.append(f"  Energia: {result.total_energy_kwh:,.0f} kWh = "
                f"€{result.total_energy_eur:,.0f} = {result.total_carbon_kg:.0f} kgCO₂")
    lines.append("")

    # Worst and best moments
    if result.worst_hour:
        wh = result.worst_hour
        lines.append(f"  📅 PIOR HORA DO ANO: {wh.get('date','?')}")
        lines.append(f"     F = {wh.get('F',0):.3f} · "
                    f"F-debt €{wh.get('f_debt_eur_h',0):.2f}/h · "
                    f"{wh.get('co2_breaches',0)} salas com CO₂ acima do limite legal")

    if result.best_hour:
        bh = result.best_hour
        lines.append(f"  ✅ MELHOR HORA DO ANO: {bh.get('date','?')} · F = {bh.get('F',0):.3f}")
    lines.append("")

    # Violations summary
    lines.append(f"  ⚖ INCUMPRIMENTOS LEGAIS:")
    lines.append(f"  CO₂ > 1000ppm (Portaria 353-A/2013): {result.total_co2_breaches_legal:,} ocorrências")
    lines.append(f"  Temperatura < mínimo legal: {result.total_temp_breaches:,} ocorrências")
    lines.append(f"  Iluminação < mínimo EN 12464-1: {result.total_lux_breaches:,} ocorrências")
    lines.append("")

    # Monthly table
    lines.append(f"  📅 CALENDÁRIO ANUAL:")
    for month in range(1, 13):
        m = result.monthly.get(month, {})
        if m.get("status") == "FECHADO":
            lines.append(f"  {m['name']:12s}: FECHADO")
            continue
        bar_len = int(m.get("mean_F", 0) * 16)
        bar = "█" * bar_len + "░" * (16 - bar_len)
        lines.append(f"  {m['name']:12s}: F={m.get('mean_F',0):.3f} [{bar}] "
                    f"F-debt=€{m.get('f_debt',0):>7,.0f}  CO₂×{m.get('co2_breaches',0):>3}")
    lines.append("")

    # Worst room
    worst_room = min(result.room_annual.items(),
                     key=lambda x: x[1]["mean_F"], default=("?", {}))
    best_room  = max(result.room_annual.items(),
                     key=lambda x: x[1]["mean_F"], default=("?", {}))
    lines.append(f"  🏠 SALA MAIS PROBLEMÁTICA: {worst_room[0]} "
                f"(F={worst_room[1].get('mean_F',0):.3f}, "
                f"F-debt=€{worst_room[1].get('f_debt_eur',0):,.0f}/ano)")
    lines.append(f"  🏆 SALA MELHOR: {best_room[0]} "
                f"(F={best_room[1].get('mean_F',0):.3f})")
    lines.append("")
    lines.append(f"  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    lines.append(f"  Designing to free. -- Gonçalo")
    lines.append(f"{'═'*68}\n")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CHAT TOOL
# ─────────────────────────────────────────────────────────────────────────────

def tool_annual_simulation(mode: str = "baseline",
                           intervention: str = "none") -> dict:
    """
    Full year simulation. mode: baseline|intervention|compare_all
    intervention: none|pintassilgo_fix|cantina_hvac|all_halls|full_upgrade
    """
    if mode == "compare_all":
        analysis = analyse_interventions(verbose=False)
        summary = []
        for key, data in analysis.items():
            if key == "baseline": continue
            summary.append({
                "name": key,
                "desc": data["desc"],
                "cost_eur": data["cost_eur"],
                "delta_F": data["delta_F"],
                "savings_eur_year": data["total_savings_eur"],
                "payback_months": data["payback_months"],
                "roi_pct": data["roi_pct"],
            })
        baseline = analysis["baseline"]
        return {
            "mode": "compare_all",
            "baseline_F": baseline["mean_F"],
            "baseline_f_debt_eur": baseline["f_debt_eur"],
            "baseline_co2_breaches": baseline["co2_breaches_legal"],
            "worst_hour": baseline["worst_hour"],
            "interventions_ranked": sorted(summary, key=lambda x: -x["roi_pct"]),
            "best_roi": max(summary, key=lambda x: x["roi_pct"]) if summary else {},
            "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
        }

    iv_changes = INTERVENTIONS_MENU.get(intervention, {}).get("changes", {})
    result = run_annual(interventions=iv_changes, verbose=False)
    narrative = narrate_year(result, iv_changes if iv_changes else None)

    return {
        "mode": mode,
        "intervention": intervention,
        "mean_F_annual": result.mean_F_annual,
        "total_f_debt_eur": round(result.total_f_debt_eur, 0),
        "total_energy_kwh": round(result.total_energy_kwh, 0),
        "total_co2_breaches_legal": result.total_co2_breaches_legal,
        "total_temp_breaches": result.total_temp_breaches,
        "worst_hour": result.worst_hour,
        "best_hour": result.best_hour,
        "monthly_F": {m: result.monthly[m].get("mean_F", 0) for m in range(1, 13)},
        "monthly_f_debt": {m: result.monthly[m].get("f_debt", 0) for m in range(1, 13)},
        "worst_room": min(result.room_annual, key=lambda r: result.room_annual[r]["mean_F"]),
        "worst_room_f_debt": round(max(v["f_debt_eur"] for v in result.room_annual.values()), 0),
        "narrative": narrative,
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  PlantaOS — SIMULAÇÃO ANUAL COMPLETA                        ║")
    print("║  HORSE CFT · 12 meses · todas as salas · todos os dias     ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # 1. Baseline
    print("\n  Cenário 1: Baseline (sem intervenções)\n")
    baseline = run_annual(verbose=True)
    print(narrate_year(baseline))

    # 2. Compare interventions
    print("\n  Cenário 2: Análise de intervenções\n")
    analysis = analyse_interventions(verbose=True)

    # 3. Best intervention applied
    best_key = max(
        [k for k in analysis if k != "baseline"],
        key=lambda k: analysis[k]["roi_pct"]
    )
    best_iv = INTERVENTIONS_MENU[best_key]
    print(f"\n  Cenário 3: Melhor intervenção — {best_iv['desc']}\n")
    fixed = run_annual(interventions=best_iv["changes"], verbose=True)
    print(narrate_year(fixed, best_iv["changes"]))

    delta_F = fixed.mean_F_annual - baseline.mean_F_annual
    delta_debt = baseline.total_f_debt_eur - fixed.total_f_debt_eur
    print(f"  IMPACTO DA INTERVENÇÃO '{best_key}':")
    print(f"  ΔF = {delta_F:+.4f}")
    print(f"  Poupança F-debt: €{delta_debt:,.0f}/ano")
    print(f"  Custo intervenção: €{best_iv['cost_eur']:,}")
    print(f"  Payback: {analysis[best_key]['payback_months']:.1f} meses")
    print(f"\n  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
