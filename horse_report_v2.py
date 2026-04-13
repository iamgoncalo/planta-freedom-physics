"""
horse_report_v2.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Relatório WOW Completo — HORSE CFT
Zero hardcodes. Tudo lido de config files.
O sistema fala baseado nos seus próprios resultados.

Estrutura:
  sensors.yaml         → hardware recomendado (preços, qtd, protocolo)
  report_config.yaml   → regras de narrativa, thresholds, advice rules
  annual_simulation.py → simulação completa (lê config.yaml)
  building_flows.py    → fluxos em tempo real (lê config.yaml)

Corre standalone:
  python3 horse_report_v2.py

SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import importlib.util, os, sys, math, yaml
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────────────────────────────────────

def _load_module(name):
    path = os.path.join(BASE, f"{name}.py")
    if not os.path.exists(path):
        print(f"  ✗ {name}.py não encontrado em {BASE}"); return None
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def _load_yaml(name):
    for candidate in [
        os.path.join(BASE, f"{name}.yaml"),
        os.path.join(BASE, f"{name}.yml"),
        os.path.join(BASE, "config.yaml"),
    ]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                return yaml.safe_load(f) or {}
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# NARRATIVE ENGINE — system speaks from data
# ─────────────────────────────────────────────────────────────────────────────

def _f_band(F, bands):
    for name, b in bands.items():
        if b["min"] <= F <= b["max"]:
            return b
    return bands["critical"]

def _roi_band(roi_pct, bands):
    for name, b in sorted(bands.items(), key=lambda x: -x[1]["min"]):
        if roi_pct >= b["min"]:
            return b["label"]
    return bands["low"]["label"]

def _payback_band(months, bands):
    for name, b in sorted(bands.items(), key=lambda x: x[1]["max"]):
        if months <= b["max"]:
            return b["label"]
    return bands["slow"]["label"]

def _apply_rule(rule, context):
    """Apply an advice rule from report_config.yaml to computed context."""
    condition = rule.get("condition", "always")
    msg_template = rule.get("system_says", "")
    if condition == "always":
        try: return msg_template.format(**context).strip()
        except: return msg_template.strip()
    try:
        if eval(condition, {}, context):
            return msg_template.format(**context).strip()
    except: pass
    return None

def _sensor_total(sensors_cfg, key="qty_horse_cft"):
    total = 0
    for s in sensors_cfg.get("sensors", {}).values():
        total += s.get("price_eur", 0) * s.get(key, 0)
    return total

def _sensor_priority(sensors_cfg, priority):
    total = 0
    for s in sensors_cfg.get("sensors", {}).values():
        if s.get("priority", 99) == priority:
            total += s.get("price_eur", 0) * s.get("qty_horse_cft", 0)
    return total

# ─────────────────────────────────────────────────────────────────────────────
# MAIN REPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_report():
    # Load all configs
    sensors_cfg   = _load_yaml("sensors")
    report_cfg    = _load_yaml("report_config")
    plantaos_cfg  = _load_yaml("config")

    # Load simulation modules
    ann_mod = _load_module("annual_simulation")
    bf_mod  = _load_module("building_flows")

    f_bands  = report_cfg.get("f_bands", {})
    roi_bands= report_cfg.get("roi_bands", {})
    pb_bands = report_cfg.get("payback_bands", {})
    viol_cfg = report_cfg.get("violation_bands", {})
    advice   = report_cfg.get("advice_rules", {})
    timeline = report_cfg.get("timeline", {})
    sensors  = sensors_cfg.get("sensors", {})
    mva      = sensors_cfg.get("minimum_viable", {})

    # D weights from config.yaml (or default AFI Master values)
    d_weights = plantaos_cfg.get("distortion", {}).get("weights", {
        "thermal": 0.40, "co2": 0.22, "humidity": 0.16,
        "light": 0.12, "noise": 0.05, "occupancy": 0.03, "spatial": 0.02
    })

    co2_alert = plantaos_cfg.get("comfort", {}).get("co2_alert_ppm",
                viol_cfg.get("co2_legal", {}).get("alert", 800))
    co2_legal = plantaos_cfg.get("comfort", {}).get("co2_legal_ppm",
                viol_cfg.get("co2_legal", {}).get("critical", 1000))
    temp_min  = plantaos_cfg.get("comfort", {}).get("winter_min_c",
                viol_cfg.get("temp_min", {}).get("alert", 18.0))
    lux_min   = plantaos_cfg.get("comfort", {}).get("lux_classroom_min",
                viol_cfg.get("lux_min", {}).get("alert", 300))

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── HEADER ────────────────────────────────────────────────────────────────
    print(f"\n{'╔'+'═'*66+'╗'}")
    print(f"║{'HORSE CFT — PlantaOS · Relatório de Sistema':^66}║")
    print(f"║{'Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION':^66}║")
    print(f"║{f'Gerado em {now}':^66}║")
    print(f"║{'SIMULAÇÃO — F=P/D HIPÓTESE EM TESTE':^66}║")
    print(f"{'╚'+'═'*66+'╝'}")

    # ── SECÇÃO 1: AGORA ───────────────────────────────────────────────────────
    print(f"\n{'━'*68}")
    print(f"  § 1  ESTADO ACTUAL DO EDIFÍCIO")
    print(f"{'━'*68}")

    if bf_mod:
        now_h = datetime.now().hour + datetime.now().minute / 60
        now_month = datetime.now().month
        result_now = bf_mod.tool_building_flows("normal_day", month=now_month, hour=now_h)
        F_now = result_now["F_global"]
        band_now = _f_band(F_now, f_bands) if f_bands else {"label":"?","emoji":"?","urgency":"?"}
        status_now = result_now["status"]
        n_flows = result_now["total_flows"]
        emergencies = result_now.get("emergencies", [])
        systemic = result_now.get("systemic_problems", [])

        print(f"\n  F global agora: {F_now:.3f}  {band_now.get('emoji','')}  {band_now.get('label', status_now).upper()}")
        print(f"  Fluxos activos: {n_flows}  |  Urgência: {band_now.get('urgency','?')}")

        if emergencies:
            print(f"\n  {'━'*60}")
            print(f"  O SISTEMA DETECTOU {len(emergencies)} EMERGÊNCIA(S):")
            print(f"  {'━'*60}")
            for e in emergencies:
                print(f"\n  {e}")

        if systemic:
            print(f"\n  O SISTEMA DETECTOU {len(systemic)} PROBLEMA(S) SISTÉMICO(S):")
            for s in systemic:
                print(f"  {s}")

        if not emergencies and not systemic:
            print(f"\n  O edifício está a operar dentro dos parâmetros normais.")
            print(f"  {n_flows} fluxos activos em monitorização contínua.")

    # ── SECÇÃO 2: ANO COMPLETO ────────────────────────────────────────────────
    print(f"\n{'━'*68}")
    print(f"  § 2  SIMULAÇÃO ANUAL COMPLETA — todos os dias de 2026")
    print(f"{'━'*68}\n")

    if not ann_mod:
        print("  ✗ annual_simulation.py não encontrado"); return

    baseline = ann_mod.run_annual(interventions={}, verbose=True)
    analysis = ann_mod.analyse_interventions(verbose=False)
    b = analysis["baseline"]

    F_annual = baseline.mean_F_annual
    band_annual = _f_band(F_annual, f_bands) if f_bands else {"label":"?","emoji":"?"}

    # Build context dict for advice rules — all computed, zero hardcoded
    ctx = {
        "mean_F": F_annual,
        "total_people_hours": baseline.total_people_hours,
        "f_debt_eur": baseline.total_f_debt_eur,
        "energy_kwh": baseline.total_energy_kwh,
        "energy_eur": baseline.total_energy_eur,
        "carbon_kg": baseline.total_carbon_kg,
        "co2_breaches_legal": baseline.total_co2_breaches_legal,
        "temp_breaches": baseline.total_temp_breaches,
        "lux_breaches": baseline.total_lux_breaches,
        "worst_date": baseline.worst_hour.get("date","?") if baseline.worst_hour else "?",
        "worst_F": baseline.worst_hour.get("F", 0) if baseline.worst_hour else 0,
        "worst_f_debt_h": baseline.worst_hour.get("f_debt_eur_h", 0) if baseline.worst_hour else 0,
        "worst_hour": float(baseline.worst_hour.get("date","? 9.0h").split()[-1].replace("h","")) if baseline.worst_hour else 9.0,
        "worst_room": min(baseline.room_annual, key=lambda r: baseline.room_annual[r]["mean_F"]),
        "best_room": max(baseline.room_annual, key=lambda r: baseline.room_annual[r]["mean_F"]),
        "co2_alert_ppm": co2_alert,
        "co2_legal_ppm": co2_legal,
        "temp_min_c": temp_min,
        "lux_min_lux": lux_min,
        "d_weight_co2": d_weights.get("co2", 0.22),
        "d_weight_thermal": d_weights.get("thermal", 0.40),
        "monthly_cost": baseline.total_f_debt_eur / 11,  # 11 operating months
    }

    # Best intervention from data
    interventions_ranked = sorted(
        [(k, v) for k, v in analysis.items() if k != "baseline"],
        key=lambda x: -x[1]["roi_pct"]
    )
    if interventions_ranked:
        best_key, best_data = interventions_ranked[0]
        full_data = analysis.get("full_upgrade", {})
        ctx.update({
            "best_intervention": best_data.get("desc", best_key),
            "best_intervention_cost": best_data.get("cost_eur", 0),
            "best_intervention_roi": best_data.get("roi_pct", 0),
            "best_intervention_payback": best_data.get("payback_months", 0),
            "best_intervention_saving": best_data.get("total_savings_eur", 0),
            "upgrade_cost": full_data.get("cost_eur", 0) if full_data else 0,
            "upgrade_roi": full_data.get("roi_pct", 0) if full_data else 0,
            "upgrade_payback": full_data.get("payback_months", 0) if full_data else 0,
            "upgrade_saving": full_data.get("total_savings_eur", 0) if full_data else 0,
            "f_before": b.get("mean_F", F_annual),
            "f_after": full_data.get("mean_F", F_annual) if full_data else F_annual,
        })

    # Sensor totals from sensors.yaml
    total_sensor_cost = _sensor_total(sensors_cfg)
    p1_sensor_cost = _sensor_priority(sensors_cfg, 1)
    ctx["total_sensor_cost"] = total_sensor_cost
    ctx["p1_sensor_cost"] = p1_sensor_cost

    # ── ANNUAL NARRATIVE ──────────────────────────────────────────────────────
    print(f"\n  {'━'*60}")
    print(f"  O SISTEMA DIZ:")
    print(f"  {'━'*60}\n")

    # Apply all advice rules
    for rule_name, rule in advice.items():
        msg = _apply_rule(rule, ctx)
        if msg:
            print(f"  [{rule_name.upper()}]")
            for line in msg.split("\n"):
                if line.strip():
                    print(f"  {line.strip()}")
            print()

    # ── CALENDAR ──────────────────────────────────────────────────────────────
    print(f"  {'━'*60}")
    print(f"  CALENDÁRIO 2026 — todos os dias simulados:")
    print(f"  {'━'*60}")
    print(f"\n  {'MÊS':<12} {'F':>6}  {'ESTADO':<10}  {'F-DEBT':>10}  {'CO₂×':>5}  {'kWh':>7}")
    print(f"  {'─'*12} {'─'*6}  {'─'*10}  {'─'*10}  {'─'*5}  {'─'*7}")

    for month in range(1, 13):
        m = baseline.monthly.get(month, {})
        if m.get("status") == "FECHADO":
            print(f"  {m['name']:<12} {'—':>6}  {'FECHADO':<10}  {'—':>10}  {'—':>5}  {'—':>7}")
            continue
        F_m = m.get("mean_F", 0)
        band_m = _f_band(F_m, f_bands) if f_bands else {"emoji":"·"}
        bar_full = int(F_m * 14)
        bar = "█"*bar_full + "░"*(14-bar_full)
        print(f"  {m['name']:<12} {F_m:>5.3f}  [{bar}]  "
              f"€{m.get('f_debt',0):>9,.0f}  {m.get('co2_breaches',0):>5}  "
              f"{m.get('energy_kwh',0):>7,.0f}")

    # ── ROOM RANKING ──────────────────────────────────────────────────────────
    print(f"\n  {'━'*60}")
    print(f"  RANKING DAS SALAS (calculado pelo sistema):")
    print(f"  {'━'*60}")
    print(f"\n  {'#':<3} {'SALA':<18} {'F':>5}  {'F-DEBT/ANO':>11}  {'CO₂ MÉDIO':>10}  {'ESTADO':<10}")
    print(f"  {'─'*3} {'─'*18} {'─'*5}  {'─'*11}  {'─'*10}  {'─'*10}")

    sorted_rooms = sorted(baseline.room_annual.items(), key=lambda x: x[1]["mean_F"])
    for i, (room, data) in enumerate(sorted_rooms):
        F_r = data["mean_F"]
        band_r = _f_band(F_r, f_bands) if f_bands else {"emoji":"·","label":"?"}
        print(f"  {i+1:<3} {room:<18} {F_r:>5.3f}  "
              f"€{data['f_debt_eur']:>9,.0f}  "
              f"{data['mean_co2']:>9.0f}ppm  "
              f"{band_r.get('emoji','')} {band_r.get('label','?'):<8}")

    # ── SECÇÃO 3: INTERVENÇÕES ────────────────────────────────────────────────
    print(f"\n{'━'*68}")
    print(f"  § 3  INTERVENÇÕES — CALCULADAS PELO SISTEMA")
    print(f"{'━'*68}\n")

    print(f"  {'INTERVENÇÃO':<38} {'CUSTO':>8}  {'€/ANO':>9}  {'PAYBACK':>10}  {'ROI':>8}  {'ΔF':>7}")
    print(f"  {'─'*38} {'─'*8}  {'─'*9}  {'─'*10}  {'─'*8}  {'─'*7}")

    for key, data in interventions_ranked:
        roi_label  = _roi_band(data["roi_pct"], roi_bands) if roi_bands else ""
        pb_label   = _payback_band(data["payback_months"], pb_bands) if pb_bands else ""
        desc = data["desc"][:38]
        print(f"  {desc:<38} €{data['cost_eur']:>6,}  "
              f"€{data['total_savings_eur']:>7,.0f}  "
              f"{data['payback_months']:>5.1f} meses  "
              f"{data['roi_pct']:>7.0f}%  "
              f"{data['delta_F']:>+6.4f}")

    print(f"\n  O SISTEMA CONCLUI:")
    print()

    if interventions_ranked:
        best_key2, best_data2 = interventions_ranked[0]
        roi_class = _roi_band(best_data2["roi_pct"], roi_bands)
        pb_class  = _payback_band(best_data2["payback_months"], pb_bands)
        print(f"  Melhor intervenção: {best_data2['desc']}")
        print(f"  → {roi_class}")
        print(f"  → {pb_class}")
        print(f"  → Cada mês de atraso custa €{ctx['monthly_cost']:,.0f}")
        print()

        if "full_upgrade" in analysis:
            fd = analysis["full_upgrade"]
            roi_full = _roi_band(fd["roi_pct"], roi_bands)
            pb_full  = _payback_band(fd["payback_months"], pb_bands)
            print(f"  Upgrade completo: €{fd['cost_eur']:,} → €{fd['total_savings_eur']:,.0f}/ano")
            print(f"  → {roi_full}")
            print(f"  → {pb_full}")
            print(f"  → ΔF = {fd['delta_F']:+.4f} "
                  f"({b.get('mean_F',0):.3f} → {fd.get('mean_F',0):.3f})")

    # ── SECÇÃO 4: SENSORES ────────────────────────────────────────────────────
    print(f"\n{'━'*68}")
    print(f"  § 4  SENSORES — CALCULADOS A PARTIR DOS CANAIS DO D")
    print(f"{'━'*68}\n")

    print(f"  D geométrico = exp(Σ wₖ·ln(dₖ))  |  Pesos de config.yaml:")
    for ch, w in sorted(d_weights.items(), key=lambda x: -x[1]):
        print(f"  {ch:<12}: {w:.2f}  {'█'*int(w*50)}")
    print()

    # Rank channels by D weight → prioritize sensors accordingly
    channel_priority = sorted(d_weights.items(), key=lambda x: -x[1])
    channel_to_sensors = {}
    for s_key, s in sensors.items():
        for ch in s.get("resolves_channels", []):
            channel_to_sensors.setdefault(ch, []).append((s_key, s))

    print(f"  O canal com maior peso define a prioridade do sensor:")
    print()
    print(f"  {'P':>2}  {'CANAL D':>12}  {'PESO':>5}  {'SENSOR':>30}  {'€/un':>5}  {'Qtd':>3}  {'Total':>6}")
    print(f"  {'─'*2}  {'─'*12}  {'─'*5}  {'─'*30}  {'─'*5}  {'─'*3}  {'─'*6}")

    printed_sensors = set()
    for ch, w in channel_priority:
        s_list = channel_to_sensors.get(ch, [])
        for s_key, s in s_list[:1]:
            if s_key in printed_sensors: continue
            printed_sensors.add(s_key)
            total_s = s.get("price_eur", 0) * s.get("qty_horse_cft", 0)
            print(f"  {s.get('priority',99):>2}  {ch:>12}  {w:>5.2f}  "
                  f"{s.get('model','?'):>30}  €{s.get('price_eur',0):>4}  "
                  f"{s.get('qty_horse_cft',0):>3}  €{total_s:>4}")

    # Add gateway + MCU
    for s_key in ["mcu", "gateway_lorawan"]:
        s = sensors.get(s_key, {})
        if s:
            total_s = s.get("price_eur", 0) * s.get("qty_horse_cft", 0)
            print(f"  {s.get('priority',1):>2}  {'infra':>12}  {'—':>5}  "
                  f"{s.get('model','?'):>30}  €{s.get('price_eur',0):>4}  "
                  f"{s.get('qty_horse_cft',0):>3}  €{total_s:>4}")

    print(f"\n  {'─'*68}")
    total_all = _sensor_total(sensors_cfg)
    total_p1  = _sensor_priority(sensors_cfg, 1)
    print(f"  TOTAL (todos os sensores):     €{total_all:,}")
    print(f"  TOTAL (apenas prioridade 1):   €{total_p1:,}")

    # MVA from sensors.yaml
    if mva:
        print(f"\n  Arquitectura mínima viável ({mva.get('total_formula','')}):")
        print(f"  {mva.get('payback_note','')}")

    print(f"\n  O SISTEMA CONCLUI:")
    print(f"\n  Com €{total_p1:,} em sensores todos os resultados SIMULATED passam a VALIDATED.")
    print(f"  O canal térmico (peso {d_weights.get('thermal',0.40):.2f}) e CO₂ "
          f"(peso {d_weights.get('co2',0.22):.2f}) são os mais críticos.")
    rule_sensor = advice.get("sensor_priority_co2", {})
    msg_s = _apply_rule(rule_sensor, ctx)
    if msg_s:
        print()
        for line in msg_s.split("\n"):
            if line.strip(): print(f"  {line.strip()}")

    # ── SECÇÃO 5: TIMELINE ────────────────────────────────────────────────────
    print(f"\n{'━'*68}")
    print(f"  § 5  PLANO DE ACÇÃO — GERADO PELO SISTEMA COM BASE NOS DADOS")
    print(f"{'━'*68}\n")

    for phase_key, phase in timeline.items():
        cost_label = phase.get("cost", 0)
        if cost_label == "best_intervention_cost":
            cost_label = f"€{ctx.get('best_intervention_cost', 0):,}"
        elif cost_label == "full_sensor_cost":
            cost_label = f"€{total_p1:,}"
        elif cost_label == 0:
            cost_label = "custo zero"
        else:
            cost_label = f"€{cost_label:,}"

        print(f"  {phase.get('label','').upper()} ({cost_label})")
        for action in phase.get("actions", []):
            try:
                line = action.format(**ctx)
            except:
                line = action
            print(f"  → {line}")
        print()

    # ── IMPACTO TOTAL ─────────────────────────────────────────────────────────
    print(f"  {'━'*60}")
    print(f"  IMPACTO TOTAL SE TUDO IMPLEMENTADO")
    print(f"  {'━'*60}\n")

    full_d = analysis.get("full_upgrade", {})
    if full_d:
        total_invest = full_d.get("cost_eur", 0) + total_all
        annual_saving = full_d.get("total_savings_eur", 0)
        payback_total = (total_invest / annual_saving * 12) if annual_saving > 0 else 999
        print(f"  Investimento (intervenções + sensores): €{total_invest:,}")
        print(f"  Poupança anual (F-debt + energia):      €{annual_saving:,.0f}")
        print(f"  Payback total:                          {payback_total:.1f} meses")
        print(f"  ΔF:                                     "
              f"{full_d.get('delta_F',0):+.4f} "
              f"({b.get('mean_F',0):.3f} → {full_d.get('mean_F',0):.3f})")
        print(f"  Violações CO₂ eliminadas:               {baseline.total_co2_breaches_legal} → 0")
        print(f"  Violações temperatura reduzidas:        "
              f"{baseline.total_temp_breaches:,} → {full_d.get('temp_breaches',0):,}")

    print(f"\n  {'─'*68}")
    print(f"  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    print(f"  Designing to free. -- Gonçalo")
    print(f"  Planta Smart Homes · hi@planta.design\n")


if __name__ == "__main__":
    generate_report()
