"""
building_flows.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Flow Intelligence Engine
HORSE CFT · Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION

PHILOSOPHY:
  Thresholds are stupid. They check one point in time.
  Flows are intelligent. They see where things are going.

  STUPID:  "CO2 = 1050ppm → alert"
  SMART:   "CO2 rising 18ppm/min, 20 people, class ends in 40min
            → will hit 1200ppm in 22 minutes → open dampers NOW
            → Vasco da Gama always does this on Tuesday mornings"

  The building thinks in flows, not numbers.
  It speaks in plain language, not sensor values.

FLOW TYPES:
  RISE      — something is increasing toward a problem
  FALL      — something is decreasing toward a problem
  CASCADE   — one room affects its neighbours
  CIRCADIAN — pattern that repeats every 24h (anticipate, don't react)
  ANOMALY   — pattern that breaks from history (investigate)
  CLUSTER   — 3+ rooms same problem = systemic, not local
  RECOVERY  — problem resolving, track to completion

ALL RESULTS SIMULATION-BASED · F=P/D HYPOTHESIS UNDER TEST · seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from collections import deque

RNG = np.random.default_rng(2026)

# ─────────────────────────────────────────────────────────────────────────────
# FLOW dataclass — the core unit (not a data point, a trajectory)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Flow:
    room: str
    channel: str          # co2 | temp | lux | noise | humidity | F
    flow_type: str        # RISE | FALL | CASCADE | CIRCADIAN | ANOMALY | CLUSTER | RECOVERY
    current_value: float
    rate_per_min: float   # velocity of change
    predicted_breach: Optional[float]  # minutes until problem (None = no breach)
    threshold: float      # the limit we care about
    severity: int         # 1 (watch) | 2 (act soon) | 3 (act now) | 4 (emergency)
    bio_algorithm: str    # which biological algorithm this maps to
    plain_english: str    # what a human would say
    action: str           # what the building should do
    confidence: float     # 0–1
    label: str = "SIMULATED"


# ─────────────────────────────────────────────────────────────────────────────
# BUILDING MEMORY — rolling 30-minute history per room per channel
# ─────────────────────────────────────────────────────────────────────────────

class BuildingMemory:
    """
    Rolling history. 30 readings per room per channel (one per minute).
    Computes velocity (rate of change) and acceleration (rate of rate).
    """
    def __init__(self, window=30):
        self.window = window
        self.history = {}  # room → channel → deque of values

    def record(self, room: str, channel: str, value: float):
        key = (room, channel)
        if key not in self.history:
            self.history[key] = deque(maxlen=self.window)
        self.history[key].append(value)

    def velocity(self, room: str, channel: str) -> float:
        """Rate of change per minute over last 5 readings."""
        key = (room, channel)
        h = self.history.get(key, [])
        if len(h) < 2:
            return 0.0
        recent = list(h)[-5:]
        if len(recent) < 2:
            return 0.0
        return (recent[-1] - recent[0]) / max(1, len(recent) - 1)

    def mean(self, room: str, channel: str) -> float:
        key = (room, channel)
        h = list(self.history.get(key, []))
        return sum(h) / len(h) if h else 0.0

    def trend_slope(self, room: str, channel: str) -> float:
        """Linear regression slope over full window."""
        key = (room, channel)
        h = list(self.history.get(key, []))
        if len(h) < 3:
            return 0.0
        n = len(h)
        x = list(range(n))
        xm = sum(x) / n
        ym = sum(h) / n
        num = sum((xi - xm) * (yi - ym) for xi, yi in zip(x, h))
        den = sum((xi - xm) ** 2 for xi in x)
        return num / den if den > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION ENGINE — generates realistic building data for 24h
# ─────────────────────────────────────────────────────────────────────────────

ROOMS_CONFIG = {
    "Hall_GF":       {"area": 40,  "cap": 10,  "floor": 0, "ac": 0, "lux_base": 280, "windows": True},
    "Cantina":       {"area": 65,  "cap": 30,  "floor": 0, "ac": 0, "lux_base": 320, "windows": True},
    "Egas_Moniz":    {"area": 78,  "cap": 17,  "floor": 0, "ac": 1, "lux_base": 409, "windows": True},
    "Damasio":       {"area": 65,  "cap": 15,  "floor": 0, "ac": 1, "lux_base": 230, "windows": True},
    "Pintassilgo":   {"area": 78,  "cap": 12,  "floor": 0, "ac": 0, "lux_base": 85,  "windows": True},
    "Gago_Coutinho": {"area": 52,  "cap": 12,  "floor": 0, "ac": 1, "lux_base": 205, "windows": True},
    "Hall_F1":       {"area": 35,  "cap": 10,  "floor": 1, "ac": 0, "lux_base": 260, "windows": True},
    "Dojo_EMotor":   {"area": 65,  "cap": 10,  "floor": 1, "ac": 1, "lux_base": 290, "windows": True},
    "Vasco_da_Gama": {"area": 65,  "cap": 20,  "floor": 1, "ac": 2, "lux_base": 305, "windows": True},
    "Quintanilha":   {"area": 65,  "cap": 15,  "floor": 1, "ac": 2, "lux_base": 384, "windows": True},
    "Automacao":     {"area": 65,  "cap": 8,   "floor": 1, "ac": 1, "lux_base": 290, "windows": True},
    "Eiffage":       {"area": 65,  "cap": 14,  "floor": 1, "ac": 1, "lux_base": 295, "windows": True},
}

def _occupancy(room: str, hour: float, month: int = 3) -> int:
    """Realistic HORSE CFT occupancy profile."""
    cap = ROOMS_CONFIG[room]["cap"]
    if month == 7: return 0  # July closed
    if hour < 7.5 or hour > 19: return 0
    if room == "Cantina":
        return int(cap * (0.9 if 12 <= hour <= 13.5 else 0.1))
    if room in ("Hall_GF", "Hall_F1"):
        return int(cap * 0.3)
    # Training rooms: sessions 08:00-12:00, 13:30-17:30
    morning = 8.0 <= hour <= 12.0
    afternoon = 13.5 <= hour <= 17.5
    if morning or afternoon:
        return int(cap * RNG.uniform(0.6, 1.0))
    return int(cap * 0.1)

def _simulate_room_tick(room: str, state: dict, hour: float, month: int) -> dict:
    """Simulate one-minute tick for a room. Returns updated state."""
    cfg = ROOMS_CONFIG[room]
    n = _occupancy(room, hour, month)
    vol = cfg["area"] * 3.0  # 3m ceiling
    T_out = 8.0 + 8.0 * math.sin(2 * math.pi * (month - 1) / 12)  # Aveiro seasonal
    T_diurnal = 3.0 * math.sin(2 * math.pi * (hour - 6) / 24)

    # Temperature dynamics
    T_sp = 20.0 if month <= 4 or month >= 10 else 24.0
    T = state.get("T", T_sp)
    if cfg["ac"] > 0 and n > 0:
        T += (T_sp - T) * 0.05 + (T_out - T) * 0.01 + n * 0.02
    else:
        T += (T_out + T_diurnal - T) * 0.02 + n * 0.03
    T += RNG.normal(0, 0.1)

    # CO2 dynamics
    co2 = state.get("co2", 420.0)
    ach = 0.8 + (0.3 if cfg["windows"] else 0)
    co2 += n * 18.0 / vol - (co2 - 420) * ach / 60
    co2 = max(420.0, co2 + RNG.normal(0, 5))

    # Humidity
    rh = state.get("rh", 50.0)
    rh += n * 0.3 - (rh - 45) * 0.02 + RNG.normal(0, 0.5)
    rh = max(20.0, min(90.0, rh))

    # Lux
    lights_on = 8 <= hour <= 19 and n > 0
    lux = cfg["lux_base"] if lights_on else 0.0

    # Noise
    noise = 38 + n * 0.9 + RNG.normal(0, 2)

    return {"T": round(T, 2), "co2": round(co2, 1), "rh": round(rh, 1),
            "lux": round(lux, 0), "noise": round(noise, 1),
            "n_people": n, "cap": cfg["cap"], "floor": cfg["floor"], "ac": cfg["ac"]}


# ─────────────────────────────────────────────────────────────────────────────
# FLOW DETECTOR — turns trajectories into flows
# ─────────────────────────────────────────────────────────────────────────────

def _predict_breach(current: float, rate: float, limit: float) -> Optional[float]:
    """Minutes until current value crosses limit at current rate. None if safe."""
    if rate <= 0 and current < limit: return None
    if rate >= 0 and current < limit: return None
    if current >= limit: return 0.0
    if abs(rate) < 0.01: return None
    mins = (limit - current) / rate
    return round(mins, 1) if 0 < mins < 120 else None

def _plain_english_flow(room: str, channel: str, flow_type: str,
                        current: float, rate: float, breach_mins: Optional[float],
                        severity: int, action: str) -> str:
    """Generate natural language description of a flow."""
    channel_names = {
        "co2": "CO₂", "T": "temperatura", "lux": "iluminação",
        "noise": "ruído", "rh": "humidade", "F": "liberdade"
    }
    ch = channel_names.get(channel, channel)
    units = {"co2": "ppm", "T": "°C", "lux": "lux", "noise": "dB", "rh": "%", "F": ""}
    unit = units.get(channel, "")

    if flow_type == "RISE" and breach_mins:
        return (f"{room}: {ch} a subir ({current:.0f}{unit}, +{rate:.1f}/min). "
                f"Vai atingir o limite em {breach_mins:.0f} minutos. {action}.")
    elif flow_type == "RISE":
        return f"{room}: {ch} em subida ({current:.0f}{unit}, +{rate:.1f}/min). {action}."
    elif flow_type == "FALL" and breach_mins:
        return (f"{room}: {ch} a descer ({current:.0f}{unit}, {rate:.1f}/min). "
                f"Vai atingir o mínimo em {breach_mins:.0f} minutos. {action}.")
    elif flow_type == "FALL":
        return f"{room}: {ch} em queda ({current:.0f}{unit}, {rate:.1f}/min). {action}."
    elif flow_type == "CASCADE":
        return f"{room}: {ch} a propagar-se das salas adjacentes. {action}."
    elif flow_type == "CIRCADIAN":
        return f"{room}: padrão circadiano de {ch} — antecipar, não reagir. {action}."
    elif flow_type == "ANOMALY":
        return f"{room}: {ch} fora do padrão normal ({current:.0f}{unit}). {action}."
    elif flow_type == "CLUSTER":
        return f"CLUSTER: {ch} elevado em múltiplas salas — problema sistémico. {action}."
    elif flow_type == "RECOVERY":
        return f"{room}: {ch} a recuperar ({current:.0f}{unit}). {action}."
    return f"{room}: {ch} = {current:.0f}{unit}. {action}."

def detect_flows(room: str, state: dict, memory: BuildingMemory,
                 hour: float, all_states: dict) -> list:
    """Detect all active flows in a room. Returns list of Flow objects."""
    flows = []
    co2 = state["co2"]
    T = state["T"]
    lux = state["lux"]
    n = state["n_people"]
    cap = state["cap"]
    month = state.get("month", 3)

    # ── CO2 RISE FLOW ─────────────────────────────────────────────────────────
    co2_rate = memory.velocity(room, "co2")
    if co2_rate > 2.0 or co2 > 700:
        breach_alert = _predict_breach(co2, co2_rate, 800)
        breach_legal = _predict_breach(co2, co2_rate, 1000)
        breach = breach_legal if co2 > 750 else breach_alert
        severity = 4 if co2 > 1000 else (3 if co2 > 850 or (breach and breach < 10) else
                   2 if co2 > 700 or (breach and breach < 25) else 1)
        actions = {
            4: "ABRIR VENTILAÇÃO MÁXIMA AGORA. Limite legal ultrapassado.",
            3: "Aumentar ventilação agora. Vai ultrapassar o limite em breve.",
            2: "Preparar aumento de ventilação.",
            1: "Monitorizar CO₂.",
        }
        flows.append(Flow(
            room=room, channel="co2", flow_type="RISE",
            current_value=co2, rate_per_min=co2_rate,
            predicted_breach=breach, threshold=1000.0, severity=severity,
            bio_algorithm="A10 CO2 Room Alert / A01 CO2 Trigger Breath",
            plain_english=_plain_english_flow(room, "co2", "RISE", co2, co2_rate,
                                              breach, severity, actions[severity]),
            action=actions[severity], confidence=0.92, label="SIMULATED"
        ))

    # ── TEMPERATURE FALL FLOW ─────────────────────────────────────────────────
    T_rate = memory.velocity(room, "T")
    T_sp = 20.0 if month <= 4 or month >= 10 else 24.0
    T_min = 18.0 if month <= 4 or month >= 10 else 22.0
    if T_rate < -0.1 or T < T_min + 1:
        breach = _predict_breach(-T, -T_rate, -T_min) if T_rate < 0 else (
            0.0 if T < T_min else None)
        severity = 4 if T < T_min - 1 else (3 if T < T_min else
                   2 if T < T_min + 1 else 1)
        actions_T = {
            4: "LIGAR AQUECIMENTO MÁXIMO. Temperatura abaixo do mínimo legal.",
            3: "Activar aquecimento agora.",
            2: "Aumentar setpoint preventivamente.",
            1: "Temperatura a descer — monitorizar.",
        }
        if T_rate < -0.05 or T < T_min + 1:
            flows.append(Flow(
                room=room, channel="T", flow_type="FALL",
                current_value=T, rate_per_min=T_rate,
                predicted_breach=breach, threshold=T_min, severity=severity,
                bio_algorithm="A12 Shiver Heat / A14 Vasoconstriction",
                plain_english=_plain_english_flow(room, "T", "FALL", T, T_rate,
                                                  breach, severity, actions_T[severity]),
                action=actions_T[severity], confidence=0.88, label="SIMULATED"
            ))

    # ── LUX DEFICIT FLOW ──────────────────────────────────────────────────────
    if lux < 300 and n > 0:
        severity = 4 if lux < 100 else (3 if lux < 150 else 2 if lux < 200 else 1)
        lux_action = {
            4: "LUZES CRÍTICAS — abaixo de 100 lux. Risco de segurança.",
            3: "Aumentar iluminação urgentemente. Abaixo do mínimo EN 12464-1.",
            2: "Aumentar iluminação — abaixo do mínimo para sala de aula.",
            1: "Iluminação reduzida — verificar.",
        }
        if room == "Pintassilgo":
            flows.append(Flow(
                room=room, channel="lux", flow_type="ANOMALY",
                current_value=lux, rate_per_min=0.0,
                predicted_breach=None, threshold=300.0, severity=4,
                bio_algorithm="HL-05 Pintassilgo Block",
                plain_english=f"Pintassilgo: iluminação estruturalmente deficiente ({lux:.0f} lux = "
                              f"71.6% abaixo do mínimo). Sala bloqueada até upgrade de iluminação.",
                action="BLOQUEAR SALA. Nenhum grupo aqui enquanto não houver upgrade.",
                confidence=1.0, label="SIMULATED"
            ))
        else:
            flows.append(Flow(
                room=room, channel="lux", flow_type="FALL",
                current_value=lux, rate_per_min=0.0,
                predicted_breach=None, threshold=300.0, severity=severity,
                bio_algorithm="A55 Colour Warning",
                plain_english=_plain_english_flow(room, "lux", "FALL", lux, 0,
                                                  None, severity, lux_action[severity]),
                action=lux_action[severity], confidence=0.95, label="SIMULATED"
            ))

    # ── CIRCADIAN ANTICIPATION ────────────────────────────────────────────────
    # Pre-heat before morning occupancy (A18)
    if 7.0 <= hour <= 8.0 and T < T_sp - 1.0 and cap > 0:
        flows.append(Flow(
            room=room, channel="T", flow_type="CIRCADIAN",
            current_value=T, rate_per_min=T_rate,
            predicted_breach=None, threshold=T_sp, severity=1,
            bio_algorithm="A18 Circadian Temp Cycle / A66 Pre-Dawn",
            plain_english=f"{room}: pré-aquecimento circadiano — aula começa em "
                         f"{int((8.5 - hour) * 60)} minutos, temperatura actual {T:.1f}°C. "
                         f"Activar HVAC agora para chegar aos {T_sp:.0f}°C a tempo.",
            action=f"Ligar HVAC agora. Objectivo: {T_sp:.0f}°C às 08:30.",
            confidence=0.97, label="SIMULATED"
        ))

    # ── CASCADE DETECTION ─────────────────────────────────────────────────────
    # If floor neighbours have same problem
    floor = ROOMS_CONFIG[room]["floor"]
    same_floor_cold = [r for r, s in all_states.items()
                       if r != room and ROOMS_CONFIG.get(r, {}).get("floor") == floor
                       and s.get("T", 20) < T_min - 0.5]
    if len(same_floor_cold) >= 2 and T < T_min:
        flows.append(Flow(
            room=room, channel="T", flow_type="CASCADE",
            current_value=T, rate_per_min=T_rate,
            predicted_breach=None, threshold=T_min, severity=3,
            bio_algorithm="A22 Inflammation Isolation / A47 Interferon",
            plain_english=f"CASCATA: {len(same_floor_cold)+1} salas do piso {floor} "
                         f"estão frias ao mesmo tempo ({', '.join(same_floor_cold[:2])} + {room}). "
                         f"Isto não é coincidência — é falha de HVAC do piso.",
            action="Verificar central HVAC do piso. Problema sistémico, não local.",
            confidence=0.85, label="SIMULATED"
        ))

    return flows


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER DETECTOR — building-level flows
# ─────────────────────────────────────────────────────────────────────────────

def detect_clusters(all_flows: dict) -> list:
    """Detect clusters: 3+ rooms with same problem = systemic."""
    clusters = []
    channel_counts = {}
    for room, flows in all_flows.items():
        for f in flows:
            key = (f.channel, f.flow_type, f.severity)
            channel_counts.setdefault(key, []).append(room)

    for (channel, flow_type, severity), rooms in channel_counts.items():
        if len(rooms) >= 3:
            ch_names = {"co2": "CO₂", "T": "temperatura", "lux": "iluminação"}
            ch = ch_names.get(channel, channel)
            clusters.append(Flow(
                room="BUILDING", channel=channel, flow_type="CLUSTER",
                current_value=len(rooms), rate_per_min=0.0,
                predicted_breach=None, threshold=3.0, severity=min(4, severity + 1),
                bio_algorithm="A43 Local Inflammation / A80 Social Homeostasis",
                plain_english=f"PROBLEMA SISTÉMICO: {ch} crítico em {len(rooms)} salas "
                             f"({', '.join(rooms[:3])}{'...' if len(rooms)>3 else ''}). "
                             f"Não é um problema de sala — é um problema de edifício.",
                action=f"Verificar sistema central de {ch}. Intervenção imediata.",
                confidence=0.90, label="SIMULATED"
            ))
    return clusters


# ─────────────────────────────────────────────────────────────────────────────
# NARRATIVE GENERATOR — turns flows into a story
# ─────────────────────────────────────────────────────────────────────────────

def narrate(all_flows: dict, clusters: list, hour: float,
            all_states: dict, tick: int) -> str:
    """Generate the building narrative in plain Portuguese."""
    lines = []
    lines.append(f"\n{'═'*68}")
    lines.append(f"  HORSE CFT · {int(hour):02d}:{int((hour%1)*60):02d}h · Tick {tick}")
    lines.append(f"  PlantaOS — Edifício a pensar em fluxos, não em dados")
    lines.append(f"{'═'*68}\n")

    # Emergency first (severity 4)
    emergencies = [(r, f) for r, flows in all_flows.items()
                   for f in flows if f.severity == 4]
    if emergencies:
        lines.append("  🚨 EMERGÊNCIAS:")
        for room, f in emergencies:
            lines.append(f"  {f.plain_english}")
            lines.append(f"     → {f.bio_algorithm}")
        lines.append("")

    # Clusters (systemic)
    if clusters:
        lines.append("  ⚠ PROBLEMAS SISTÉMICOS (múltiplas salas):")
        for c in clusters:
            lines.append(f"  {c.plain_english}")
        lines.append("")

    # Severity 3 (act now)
    urgent = [(r, f) for r, flows in all_flows.items()
              for f in flows if f.severity == 3]
    if urgent:
        lines.append("  ⚡ ACTUAR AGORA:")
        for room, f in urgent[:4]:
            lines.append(f"  {f.plain_english}")
        lines.append("")

    # Circadian (anticipate)
    circadian = [(r, f) for r, flows in all_flows.items()
                 for f in flows if f.flow_type == "CIRCADIAN"]
    if circadian:
        lines.append("  🌅 ANTECIPAÇÃO CIRCADIANA:")
        for room, f in circadian[:3]:
            lines.append(f"  {f.plain_english}")
        lines.append("")

    # Building F score
    F_scores = [s.get("F", 0.5) for s in all_states.values() if s.get("n_people", 0) > 0]
    if F_scores:
        F_global = sum(F_scores) / len(F_scores)
        n_people = sum(s.get("n_people", 0) for s in all_states.values())
        status = ("óptimo" if F_global > 0.8 else "bom" if F_global > 0.65
                  else "degradado" if F_global > 0.5 else "crítico")
        lines.append(f"  📊 ESTADO GLOBAL:")
        lines.append(f"  F = {F_global:.3f} ({status}) · {n_people} pessoas · "
                    f"{len([f for flows in all_flows.values() for f in flows])} fluxos activos")
        lines.append(f"  O edifício {'respira bem' if F_global > 0.7 else 'precisa de atenção'}.")
        lines.append("")

    lines.append(f"  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    lines.append(f"  Designing to free. -- Gonçalo")
    lines.append(f"{'═'*68}\n")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# F SCORE — simple geometric (matches PlantaOS HL-11)
# ─────────────────────────────────────────────────────────────────────────────

def compute_F(state: dict, month: int = 3) -> float:
    T_sp = 20.0 if month <= 4 or month >= 10 else 24.0
    d_temp = max(1.0, 1.0 + abs(state["T"] - T_sp) / 2.5)
    d_co2  = max(1.0, state["co2"] / 700.0)
    d_lux  = max(1.0, 400.0 / max(state["lux"], 10.0)) if state["n_people"] > 0 else 1.0
    d_rh   = max(1.0, 1.0 + abs(state["rh"] - 50) / 15.0)
    d_noise= max(1.0, 1.0 + max(0, state["noise"] - 45) / 10.0)
    W = {"T": 0.40, "co2": 0.22, "lux": 0.12, "rh": 0.16, "noise": 0.05}
    ln_D = (W["T"]*math.log(d_temp) + W["co2"]*math.log(d_co2) +
            W["lux"]*math.log(d_lux) + W["rh"]*math.log(d_rh) +
            W["noise"]*math.log(d_noise))
    D = math.exp(ln_D)
    P = 0.5 + 0.5 * (state.get("n_people", 1) / max(1, state["cap"]))
    return round(min(1.0, max(0.0, P / D)), 4)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SIMULATION — runs a full day and returns flows
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation(month: int = 3, target_hour: float = None,
                   n_ticks: int = 60, verbose: bool = True) -> dict:
    """
    Run building flow simulation.
    month: 1-12 (7=closed)
    target_hour: if set, simulate to this hour and return state
    n_ticks: minutes to simulate
    """
    memory = BuildingMemory(window=30)
    states = {r: {"T": 18.0, "co2": 420.0, "rh": 50.0, "lux": 0.0,
                  "noise": 38.0, "n_people": 0, "cap": cfg["cap"],
                  "floor": cfg["floor"], "ac": cfg["ac"], "month": month}
              for r, cfg in ROOMS_CONFIG.items()}

    start_hour = target_hour - n_ticks / 60.0 if target_hour else 7.0
    if start_hour < 0: start_hour = 0.0
    current_hour = start_hour

    all_narratives = []
    final_flows = {}
    final_clusters = []

    for tick in range(n_ticks):
        current_hour = start_hour + tick / 60.0

        # Update all rooms
        for room in ROOMS_CONFIG:
            states[room] = _simulate_room_tick(room, states[room], current_hour, month)
            states[room]["month"] = month
            states[room]["F"] = compute_F(states[room], month)

            # Record to memory
            for ch in ["co2", "T", "lux", "rh", "noise"]:
                memory.record(room, ch, states[room][ch])

        # Detect flows (every 5 ticks to avoid noise)
        if tick % 5 == 0:
            all_flows = {}
            for room in ROOMS_CONFIG:
                all_flows[room] = detect_flows(room, states[room], memory,
                                               current_hour, states)
            clusters = detect_clusters(all_flows)

            if verbose and tick % 15 == 0:
                print(narrate(all_flows, clusters, current_hour, states, tick))

            final_flows = all_flows
            final_clusters = clusters

    return {
        "final_states": states,
        "flows": final_flows,
        "clusters": final_clusters,
        "hour": current_hour,
        "month": month,
        "narrative": narrate(final_flows, final_clusters, current_hour, states, n_ticks),
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CHAT TOOL — callable from chat.py
# ─────────────────────────────────────────────────────────────────────────────

def tool_building_flows(scenario: str = "morning_crisis",
                        month: int = 3,
                        hour: float = 9.0) -> dict:
    """
    Chat-callable building flow simulation.
    scenario: morning_crisis | normal_day | evening | winter_cold | summer_heat
    """
    scenarios = {
        "morning_crisis": {"month": 1, "hour": 8.5,  "n_ticks": 45,
                          "desc": "Janeiro 08:30 — edifício a arrancar, frio, CO2 a subir"},
        "normal_day":     {"month": 3, "hour": 10.0, "n_ticks": 30,
                          "desc": "Março 10:00 — aulas em curso, estado normal"},
        "evening":        {"month": 5, "hour": 17.5, "n_ticks": 20,
                          "desc": "Maio 17:30 — fim de dia, salas a esvaziar"},
        "winter_cold":    {"month": 12,"hour": 9.0,  "n_ticks": 60,
                          "desc": "Dezembro 09:00 — frio intenso, teste de aquecimento"},
        "summer_heat":    {"month": 7, "hour": 12.0, "n_ticks": 10,
                          "desc": "Julho — edifício FECHADO"},
    }

    cfg = scenarios.get(scenario, scenarios["morning_crisis"])
    result = run_simulation(month=cfg["month"], target_hour=cfg["hour"],
                           n_ticks=cfg["n_ticks"], verbose=False)

    # Summarise for chat
    active_flows = [(r, f) for r, flows in result["flows"].items() for f in flows]
    emergencies = [f.plain_english for _, f in active_flows if f.severity == 4]
    urgent = [f.plain_english for _, f in active_flows if f.severity == 3]
    watching = [f.plain_english for _, f in active_flows if f.severity <= 2]
    cluster_msgs = [c.plain_english for c in result["clusters"]]

    F_scores = [s.get("F", 0.5) for s in result["final_states"].values()
                if s.get("n_people", 0) > 0]
    F_global = sum(F_scores) / len(F_scores) if F_scores else 0.5

    return {
        "scenario": scenario,
        "description": cfg["desc"],
        "F_global": round(F_global, 3),
        "status": ("óptimo" if F_global > 0.8 else "bom" if F_global > 0.65
                   else "degradado" if F_global > 0.5 else "crítico"),
        "total_flows": len(active_flows),
        "emergencies": emergencies,
        "urgent": urgent,
        "watching": watching[:5],
        "systemic_problems": cluster_msgs,
        "narrative": result["narrative"],
        "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST",
    }


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  PlantaOS — FLOW INTELLIGENCE ENGINE                        ║")
    print("║  O edifício pensa em fluxos, não em dados                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    for scenario in ["morning_crisis", "normal_day", "winter_cold"]:
        print(f"\n{'─'*68}")
        print(f"  CENÁRIO: {scenario}")
        result = tool_building_flows(scenario)
        print(result["narrative"])
        if result["emergencies"]:
            print("  EMERGÊNCIAS:")
            for e in result["emergencies"]:
                print(f"    {e}")
        if result["systemic_problems"]:
            print("  PROBLEMAS SISTÉMICOS:")
            for s in result["systemic_problems"]:
                print(f"    {s}")
        print(f"  F global = {result['F_global']} ({result['status']})")
        print(f"  {result['total_flows']} fluxos activos")
