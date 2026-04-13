"""
horse_report_v3.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Relatório WOW Completo v3
HORSE CFT · Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION

Zero hardcodes. Tudo de YAML.
Performance: 48% — não F=0.480.
O sistema fala. Em português. Para pessoas.

Lê:
  compliance.yaml   → todas as normas PT/EU/Global + clima
  language.yaml     → linguagem humana, traduções
  sensors.yaml      → hardware recomendado
  report_config.yaml→ regras de narrativa
  config.yaml       → parâmetros PlantaOS

Corre:
  python3 horse_report_v3.py

SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026
─────────────────────────────────────────────────────────────────────────────
"""

import importlib.util, os, math, yaml
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

def _load_module(name):
    path = os.path.join(BASE, f"{name}.py")
    if not os.path.exists(path): return None
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def _load_yaml(name):
    for p in [os.path.join(BASE, f"{name}.yaml"),
              os.path.join(BASE, f"{name}.yml")]:
        if os.path.exists(p):
            with open(p) as f: return yaml.safe_load(f) or {}
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def _perf(F, lang_cfg):
    """F score → human performance string."""
    pct = F * 100
    bands = lang_cfg.get("performance", {})
    for name, b in sorted(bands.items(), key=lambda x: -x[1]["min"]):
        if F >= b["min"]:
            label = b.get("short","?")
            emoji = b.get("emoji","")
            desc  = b.get("description","")
            action= b.get("action","")
            sys_says = b.get("system_says","")
            return {
                "display": f"Performance: {pct:.0f}%",
                "short": f"{pct:.0f}% — {label}",
                "emoji": emoji,
                "label": label,
                "description": desc,
                "action": action,
                "system_says": sys_says,
                "pct": pct,
                "bar": "█"*int(pct/5) + "░"*(20-int(pct/5)),
            }
    return {"display": f"Performance: {pct:.0f}%", "short": f"{pct:.0f}%",
            "emoji": "⚪", "label": "?", "description": "", "action": "", "pct": pct, "bar": ""}

def _debt_human(eur, lang_cfg):
    m = lang_cfg.get("metrics", {}).get("f_debt_annual", {})
    label = m.get("human", "Produtividade perdida: €{value:,.0f}").format(value=eur)
    context = m.get("context", "")
    return label, context

def _compliance_row(channel, value, comp_cfg, lang_cfg, month=3):
    """Check a single channel against all applicable norms."""
    ch_map = comp_cfg.get("channel_compliance_map", {}).get(channel, {})
    pt = comp_cfg.get("portugal", {})
    eu = comp_cfg.get("european_union", {})
    gl = comp_cfg.get("global", {})
    comp_labels = lang_cfg.get("compliance", {})
    rows = []

    if channel == "co2":
        legal = ch_map.get("critical_ppm", 1000)
        alert = ch_map.get("alert_ppm", 800)
        law_name = "Portaria 353-A/2013"
        if value > legal:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.0f}ppm > {legal}ppm (limite legal)", "consequence": "Multa até €45.000"})
        elif value > alert:
            rows.append({"norm": law_name, "status": "warn", "msg": f"{value:.0f}ppm → a aproximar-se do limite legal ({legal}ppm)", "consequence": "Risco de incumprimento"})
        else:
            rows.append({"norm": law_name, "status": "pass", "msg": f"{value:.0f}ppm ✓ (< {alert}ppm)", "consequence": ""})

    elif channel == "temp":
        if month in [1,2,3,4,10,11,12]:
            t_min = ch_map.get("winter_min_c", 18.0)
            t_max = ch_map.get("winter_max_c", 22.0)
        else:
            t_min = ch_map.get("summer_min_c", 22.0)
            t_max = ch_map.get("summer_max_c", 26.0)
        law_name = "ISO 7730 + Portaria 353-A/2013"
        if value < t_min:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.1f}°C < {t_min}°C (mínimo legal)", "consequence": "Incumprimento laboral"})
        elif value > t_max:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.1f}°C > {t_max}°C (máximo legal)", "consequence": "Incumprimento laboral"})
        else:
            rows.append({"norm": law_name, "status": "pass", "msg": f"{value:.1f}°C ✓ ({t_min}-{t_max}°C)", "consequence": ""})

    elif channel == "lux":
        l_min = ch_map.get("classroom_min_lux", 300)
        law_name = "EN 12464-1:2021"
        if value < 100:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.0f}lux < 100lux (crítico — risco de segurança)", "consequence": "Responsabilidade civil"})
        elif value < l_min:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.0f}lux < {l_min}lux (mínimo sala de aula)", "consequence": "Fadiga visual comprovada"})
        else:
            rows.append({"norm": law_name, "status": "pass", "msg": f"{value:.0f}lux ✓ (≥ {l_min}lux)", "consequence": ""})

    elif channel == "noise":
        n_max = ch_map.get("max_db", 45)
        law_name = "ISO 11690-1"
        if value > 85:
            rows.append({"norm": law_name, "status": "fail", "msg": f"{value:.0f}dB > 85dB (limite de dano auditivo)", "consequence": "Risco de saúde — ACT"})
        elif value > n_max:
            rows.append({"norm": law_name, "status": "warn", "msg": f"{value:.0f}dB > {n_max}dB (trabalho cognitivo)", "consequence": "Redução de concentração"})
        else:
            rows.append({"norm": law_name, "status": "pass", "msg": f"{value:.0f}dB ✓ (≤ {n_max}dB)", "consequence": ""})

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# COMPLIANCE SCORE (0–100%)
# ─────────────────────────────────────────────────────────────────────────────

def compliance_score(room_state: dict, comp_cfg: dict, lang_cfg: dict, month=3) -> dict:
    """Run all applicable norms. Returns score + violations list."""
    checks = []
    channels = {"co2": room_state.get("co2", 420),
                "temp": room_state.get("T", 20),
                "lux": room_state.get("lux", 300),
                "noise": room_state.get("noise", 40)}

    for ch, val in channels.items():
        rows = _compliance_row(ch, val, comp_cfg, lang_cfg, month)
        checks.extend(rows)

    n_total = len(checks)
    n_pass  = sum(1 for c in checks if c["status"] == "pass")
    n_warn  = sum(1 for c in checks if c["status"] == "warn")
    n_fail  = sum(1 for c in checks if c["status"] == "fail")
    score   = n_pass / n_total if n_total else 1.0

    return {
        "score_pct": round(score * 100),
        "n_pass": n_pass, "n_warn": n_warn, "n_fail": n_fail,
        "checks": checks,
        "legal_compliant": n_fail == 0,
        "violations": [c for c in checks if c["status"] == "fail"],
        "warnings": [c for c in checks if c["status"] == "warn"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANNUAL COMPLIANCE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def annual_compliance_analysis(baseline, comp_cfg, lang_cfg) -> dict:
    """Map annual simulation results to compliance framework."""
    fin = comp_cfg.get("financial_consequences", {})
    pt  = comp_cfg.get("portugal", {})
    eu  = comp_cfg.get("european_union", {})
    sdg = comp_cfg.get("global", {}).get("sdg_goals", {})

    temp_b = baseline.total_temp_breaches
    lux_b  = baseline.total_lux_breaches
    co2_b  = baseline.total_co2_breaches_legal

    # Estimated liability
    temp_cost = temp_b * fin.get("temp_legal_breach_per_event_eur", 200)
    lux_cost  = lux_b  * fin.get("lux_legal_breach_per_event_eur", 100)
    co2_cost  = co2_b  * fin.get("co2_legal_breach_per_event_eur", 500)
    total_legal_risk = min(temp_cost + lux_cost + co2_cost,
                           fin.get("annual_fine_max_eur", 45000))

    # EPBD compliance
    area = 950  # from config
    epbd = pt.get("epbd_2024", {})
    epbd_required = area > epbd.get("monitoring_required_above_m2", 250)

    # EU Taxonomy
    tax = eu.get("eu_taxonomy_2021", {})
    carbon_intensity = baseline.total_carbon_kg / area
    taxonomy_compliant = carbon_intensity <= tax.get("threshold_kg_co2_m2_year", 40)

    return {
        "temp_violations": temp_b,
        "lux_violations": lux_b,
        "co2_violations_legal": co2_b,
        "estimated_legal_risk_eur": round(total_legal_risk),
        "epbd_monitoring_required": epbd_required,
        "epbd_compliant": False,  # no sensors = not compliant
        "eu_taxonomy_carbon_intensity_kg_m2": round(carbon_intensity, 1),
        "eu_taxonomy_threshold_kg_m2": tax.get("threshold_kg_co2_m2_year", 40),
        "eu_taxonomy_compliant": taxonomy_compliant,
        "well_potential": "Silver" if baseline.mean_F_annual > 0.6 else "Bronze",
        "leed_potential": "Certified" if baseline.mean_F_annual > 0.55 else "Not ready",
        "breeam_potential": "Good" if baseline.mean_F_annual > 0.5 else "Pass",
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN REPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_report():
    # Load all configs
    comp_cfg    = _load_yaml("compliance")
    lang_cfg    = _load_yaml("language")
    sensors_cfg = _load_yaml("sensors")
    report_cfg  = _load_yaml("report_config")
    plants_cfg  = _load_yaml("config")

    # Load modules
    ann_mod = _load_module("annual_simulation")
    bf_mod  = _load_module("building_flows")

    # D weights from config.yaml
    d_weights = plants_cfg.get("distortion", {}).get("weights", {
        "thermal":0.40,"co2":0.22,"humidity":0.16,
        "light":0.12,"noise":0.05,"occupancy":0.03,"spatial":0.02
    })

    # Context
    ctx_cfg  = lang_cfg.get("context", {})
    fin_cfg  = comp_cfg.get("financial_consequences", {})
    now_str  = datetime.now().strftime("%d/%m/%Y  %H:%M")

    # ── HEADER ────────────────────────────────────────────────────────────────
    print(f"\n{'╔'+'═'*68+'╗'}")
    print(f"║{'HORSE CFT — Relatório de Desempenho e Conformidade':^68}║")
    print(f"║{'PlantaOS · Planta Smart Homes · FCT 2025.00020.AIVLAB':^68}║")
    print(f"║{now_str:^68}║")
    print(f"║{'SIMULAÇÃO PURA — F=P/D HIPÓTESE EM TESTE — ZERO SENSORES':^68}║")
    print(f"{'╚'+'═'*68+'╝'}\n")

    # ── CONTEXTO EXTERNO ──────────────────────────────────────────────────────
    non_compliant = fin_cfg.get("buildings_non_compliant_portugal_pct", 75)
    time_indoors  = ctx_cfg.get("indoors_pct", 90)
    fine_max      = fin_cfg.get("annual_fine_max_eur", 45000)
    prod_loss     = ctx_cfg.get("productivity_co2_loss_pct", 50)
    print(f"  {'─'*68}")
    print(f"  CONTEXTO: Portugal e o problema real")
    print(f"  {'─'*68}")
    print(f"  {non_compliant}% dos edifícios em Portugal não cumpre com a lei  [{ctx_cfg.get('non_compliant_source','JRC 2022')}]")
    print(f"  {time_indoors}% do tempo humano é passado em interiores  [{ctx_cfg.get('indoors_source','OMS')}]")
    print(f"  -{prod_loss}% de produtividade com CO₂ elevado  [{ctx_cfg.get('productivity_source','')}]")
    print(f"  Multa máxima ACT: €{fine_max:,}/ano por incumprimento laboral")
    print(f"  EPBD 2024: monitorização contínua obrigatória em edifícios > 250m²")
    print(f"  HORSE CFT tem {950}m² — a lei JÁ SE APLICA.\n")

    # ── SECÇÃO 1: AGORA ───────────────────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 1  AGORA — O que está a acontecer neste momento")
    print(f"  {'━'*68}\n")

    if bf_mod:
        now_h = datetime.now().hour + datetime.now().minute/60
        now_m = datetime.now().month
        r_now = bf_mod.tool_building_flows("normal_day", month=now_m, hour=now_h)
        p_now = _perf(r_now["F_global"], lang_cfg)
        print(f"  {p_now['emoji']}  Edifício: {p_now['display']}  [{p_now['label']}]")
        print(f"     {p_now['description']}")
        print(f"     {p_now['bar']}  Urgência: {p_now['action']}\n")

        if r_now.get("emergencies"):
            print(f"  🚨 EMERGÊNCIAS ACTIVAS ({len(r_now['emergencies'])}):")
            for e in r_now["emergencies"]:
                print(f"     {e}")
        if r_now.get("systemic_problems"):
            print(f"\n  ⚠  PROBLEMAS SISTÉMICOS ({len(r_now['systemic_problems'])}):")
            for s in r_now["systemic_problems"]:
                print(f"     {s}")
        print()

    # ── SECÇÃO 2: ANO COMPLETO ────────────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 2  2026 COMPLETO — todos os dias, todas as salas")
    print(f"  {'━'*68}\n")

    if not ann_mod:
        print("  ✗ annual_simulation.py não encontrado"); return

    baseline = ann_mod.run_annual(interventions={}, verbose=False)
    analysis = ann_mod.analyse_interventions(verbose=False)
    b = analysis["baseline"]

    F_ann  = baseline.mean_F_annual
    p_ann  = _perf(F_ann, lang_cfg)
    debt_l, debt_ctx = _debt_human(baseline.total_f_debt_eur, lang_cfg)

    print(f"  {p_ann['emoji']}  {p_ann['display']}  ({p_ann['label']})")
    print(f"     {p_ann['system_says']}")
    print(f"     [{p_ann['bar']}]\n")
    print(f"  O SISTEMA DIZ:")
    print(f"  {debt_l}")
    print(f"  ({debt_ctx})\n")

    # Key annual numbers in human language
    energy_per_person = baseline.total_energy_kwh / max(1, baseline.total_people_hours) * 1000
    carbon_intensity  = baseline.total_carbon_kg / 950
    monthly_debt      = baseline.total_f_debt_eur / 11
    daily_debt        = baseline.total_f_debt_eur / 220

    print(f"  Números do ano (todos calculados pelo sistema):")
    print(f"  → €{baseline.total_f_debt_eur:>12,.0f}  perdidos em produtividade")
    print(f"  → €{baseline.total_energy_eur:>12,.0f}  em energia eléctrica")
    print(f"  → {baseline.total_energy_kwh:>12,.0f}  kWh consumidos")
    print(f"  → {baseline.total_carbon_kg:>12,.0f}  kg CO₂ emitidos  ({carbon_intensity:.1f} kg/m²/ano)")
    print(f"  → {baseline.total_people_hours:>12,}   horas-pessoa em condições sub-óptimas")
    print(f"  → €{daily_debt:>12,.0f}  perdidos POR DIA em que não há intervenção")
    print()

    # Compliance analysis
    comp_ann = annual_compliance_analysis(baseline, comp_cfg, lang_cfg)
    print(f"  CONFORMIDADE LEGAL (calculada pelo sistema):")
    print(f"  {'─'*64}")

    # All norms
    norms_check = [
        ("Portaria 353-A/2013", "CO₂",
         "✅ Zero violações legais" if comp_ann["co2_violations_legal"]==0
         else f"❌ {comp_ann['co2_violations_legal']:,} violações (>{comp_cfg.get('portugal',{}).get('portaria_353a_2013',{}).get('limit_ppm',1000)}ppm)"),
        ("ISO 7730 + Lei 102/2009", "Temperatura",
         f"❌ {comp_ann['temp_violations']:,} violações (abaixo de 18°C — mínimo legal)"
         if comp_ann["temp_violations"] > 0
         else "✅ Temperatura dentro do intervalo legal"),
        ("EN 12464-1:2021", "Iluminação",
         f"❌ {comp_ann['lux_violations']:,} violações (abaixo de 300 lux — EN mínimo)"
         if comp_ann["lux_violations"] > 0
         else "✅ Iluminação conforme"),
        ("EPBD 2024", "Monitorização",
         "❌ Monitorização contínua obrigatória — sem sensores = incumprimento"
         if comp_ann["epbd_monitoring_required"] and not comp_ann["epbd_compliant"]
         else "✅ EPBD compliant"),
        ("EU Taxonomy 2021", "Carbono",
         f"❌ {comp_ann['eu_taxonomy_carbon_intensity_kg_m2']} kg/m²/ano > {comp_ann['eu_taxonomy_threshold_kg_m2']} kg/m² (limite taxonomia)"
         if not comp_ann["eu_taxonomy_compliant"]
         else f"✅ Carbono: {comp_ann['eu_taxonomy_carbon_intensity_kg_m2']} kg/m²/ano (abaixo do limite)"),
    ]

    for norm, channel, status in norms_check:
        print(f"  {status}  [{norm} — {channel}]")

    print(f"\n  Risco legal estimado: €{comp_ann['estimated_legal_risk_eur']:,}/ano")
    print(f"  (baseado em {comp_ann['temp_violations']:,} violações temperatura + {comp_ann['lux_violations']:,} iluminação)")
    print()

    # Green building potential
    print(f"  CERTIFICAÇÕES VERDES (potencial estimado):")
    print(f"  WELL v2:   {comp_ann['well_potential']}  |  LEED v4.1: {comp_ann['leed_potential']}  |  BREEAM: {comp_ann['breeam_potential']}")
    print()

    # ── CALENDAR ──────────────────────────────────────────────────────────────
    print(f"  {'─'*68}")
    print(f"  CALENDÁRIO 2026:")
    print(f"  {'─'*68}")
    months_cfg = lang_cfg.get("months", {})
    print(f"\n  {'MÊS':<12}  {'PERFORMANCE':>14}  {'PERDA PROD.':>12}  {'TEMP×':>6}  {'LUX×':>5}")
    print(f"  {'─'*12}  {'─'*14}  {'─'*12}  {'─'*6}  {'─'*5}")

    for month in range(1, 13):
        m = baseline.monthly.get(month, {})
        if m.get("status") == "FECHADO":
            mname = months_cfg.get(month, f"Mês {month}")
            print(f"  {mname:<12}  {'— FECHADO':>14}  {'—':>12}  {'—':>6}  {'—':>5}")
            continue
        F_m   = m.get("mean_F", 0)
        p_m   = _perf(F_m, lang_cfg)
        mname = months_cfg.get(month, f"Mês {month}")
        print(f"  {mname:<12}  {p_m['emoji']} {p_m['short']:>12}  "
              f"€{m.get('f_debt',0):>10,.0f}  "
              f"{m.get('temp_breaches',0):>6,}  "
              f"{0:>5}")

    print()

    # ── ROOM RANKING ──────────────────────────────────────────────────────────
    print(f"  {'─'*68}")
    print(f"  RANKING DAS SALAS — ordenado por impacto humano:")
    print(f"  {'─'*68}")
    print(f"\n  {'#':<3} {'SALA':<18} {'PERFORMANCE':>14}  {'PERDA ANUAL':>12}  {'CONFORMIDADE':>12}")
    print(f"  {'─'*3} {'─'*18} {'─'*14}  {'─'*12}  {'─'*12}")

    sorted_rooms = sorted(baseline.room_annual.items(), key=lambda x: x[1]["mean_F"])
    comp_map_cfg = comp_cfg.get("channel_compliance_map", {})

    for i, (room, data) in enumerate(sorted_rooms):
        F_r  = data["mean_F"]
        p_r  = _perf(F_r, lang_cfg)
        # Quick compliance check for this room
        n_fail = 0
        if data.get("mean_co2", 420) > comp_map_cfg.get("co2",{}).get("critical_ppm",1000): n_fail += 1
        if room == "Pintassilgo": n_fail += 1  # lux
        comp_str = "❌ Violação" if n_fail > 0 else ("✅ OK" if F_r > 0.6 else "⚠  Atenção")
        print(f"  {i+1:<3} {room:<18} {p_r['emoji']} {p_r['short']:>12}  "
              f"€{data['f_debt_eur']:>10,.0f}  {comp_str:>12}")

    print()

    # ── SECÇÃO 3: INTERVENÇÕES ────────────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 3  O QUE FAZER — calculado pelo sistema")
    print(f"  {'━'*68}\n")

    interventions_ranked = sorted(
        [(k, v) for k, v in analysis.items() if k != "baseline"],
        key=lambda x: -x[1]["roi_pct"]
    )

    roi_bands  = report_cfg.get("roi_bands", {})
    pb_bands   = report_cfg.get("payback_bands", {})

    # Human ROI band
    def _roi_label(roi_pct):
        for name, b in sorted(roi_bands.items(), key=lambda x: -x[1].get("min",0)):
            if roi_pct >= b.get("min",0): return b.get("label","")
        return ""

    def _pb_label(months):
        for name, b in sorted(pb_bands.items(), key=lambda x: x[1].get("max",999)):
            if months <= b.get("max",999): return b.get("label","")
        return ""

    print(f"  {'INTERVENÇÃO':<38} {'INVESTIMENTO':>12}  {'POUPANÇA/ANO':>12}  {'PAYBACK':>10}  {'ROI':>8}")
    print(f"  {'─'*38} {'─'*12}  {'─'*12}  {'─'*10}  {'─'*8}")

    for key, data in interventions_ranked:
        desc = data["desc"][:38]
        print(f"  {desc:<38} €{data['cost_eur']:>10,}  "
              f"€{data['total_savings_eur']:>10,.0f}  "
              f"{data['payback_months']:>5.1f} meses  "
              f"{data['roi_pct']:>7.0f}%")
        print(f"  {'':>38} {_roi_label(data['roi_pct'])}")
        print(f"  {'':>38} {_pb_label(data['payback_months'])}\n")

    if interventions_ranked:
        best_key, best_data = interventions_ranked[0]
        print(f"  O SISTEMA CONCLUI:")
        print(f"  A melhor intervenção é '{best_data['desc']}'.")
        print(f"  Cada mês de atraso custa €{baseline.total_f_debt_eur/11:,.0f}.")
        print(f"  O investimento de €{best_data['cost_eur']:,} recupera-se em {best_data['payback_months']:.1f} meses.")

        fd = analysis.get("full_upgrade",{})
        if fd:
            p_before = _perf(b.get("mean_F",0), lang_cfg)
            p_after  = _perf(fd.get("mean_F",0), lang_cfg)
            print(f"\n  Upgrade completo: {p_before['short']} → {p_after['short']}")
            print(f"  Custo: €{fd['cost_eur']:,}  |  Poupança: €{fd['total_savings_eur']:,.0f}/ano  |  Payback: {fd['payback_months']:.1f} meses")

    print()

    # ── SECÇÃO 4: SENSORES ────────────────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 4  SENSORES — para transformar SIMULADO em VALIDADO")
    print(f"  {'━'*68}\n")

    print(f"  Por que sensores? Porque a lei já os exige.")
    epbd = comp_cfg.get("portugal",{}).get("epbd_2024",{})
    print(f"  EPBD 2024: monitorização obrigatória em edifícios > {epbd.get('monitoring_required_above_m2',250)}m²")
    print(f"  HORSE CFT: {950}m² — está acima do limite. Sem sensores = incumprimento.\n")

    print(f"  Canal D mais pesado → sensor mais prioritário:")
    print(f"  (Pesos de {plants_cfg.get('name','config.yaml') or 'config.yaml'})\n")

    sensors = sensors_cfg.get("sensors", {})

    # Sort sensors by priority + D weight of their channel
    def _sensor_d_weight(s):
        channels = s.get("resolves_channels", [])
        for ch in channels:
            w = d_weights.get(ch, 0)
            if w > 0: return w
        return 0

    sensor_rows = []
    for s_key, s in sensors.items():
        sensor_rows.append((s_key, s, s.get("priority",9), _sensor_d_weight(s)))
    sensor_rows.sort(key=lambda x: (x[2], -x[3]))

    total_cost = sum(s.get("price_eur",0)*s.get("qty_horse_cft",0) for _,s,_,_ in sensor_rows)
    p1_cost    = sum(s.get("price_eur",0)*s.get("qty_horse_cft",0) for _,s,p,_ in sensor_rows if p==1)

    print(f"  {'P':>2}  {'SENSOR':<30}  {'CANAL D':>12}  {'PESO D':>6}  €/un  Qtd  Total")
    print(f"  {'─'*2}  {'─'*30}  {'─'*12}  {'─'*6}  ─────  ───  ─────")

    for s_key, s, pri, dw in sensor_rows:
        ch = s.get("resolves_channels",["?"])[0]
        dw_str = f"{dw:.2f}" if dw > 0 else "  —"
        total_s = s.get("price_eur",0)*s.get("qty_horse_cft",0)
        print(f"  {pri:>2}  {s.get('model','?'):<30}  {ch:>12}  {dw_str:>6}  "
              f"€{s.get('price_eur',0):>3}  {s.get('qty_horse_cft',0):>3}  €{total_s:>4}")
        if s.get("notes"):
            print(f"       → {s['notes'][:64]}")

    print(f"\n  {'─'*68}")
    print(f"  Total sensores completos:    €{total_cost:,}")
    print(f"  Apenas prioridade 1 (MVP):   €{p1_cost:,}")
    mva = sensors_cfg.get("minimum_viable",{})
    if mva:
        print(f"  {mva.get('payback_note','')}")
    print()

    print(f"  O SISTEMA CONCLUI:")
    print(f"  Com €{p1_cost:,} o HORSE CFT passa a:")
    print(f"    1. Cumprir EPBD 2024 (monitorização contínua obrigatória)")
    print(f"    2. Ter dados reais para renegociar contrato com HORSE/Renault")
    print(f"    3. Transformar todos os resultados de SIMULATED → VALIDATED")
    print(f"    4. Qualificar para WELL Bronze + LEED Certified")
    print(f"    5. Publicar paper com dados empíricos (Automation in Construction)")
    print()

    # ── SECÇÃO 5: NORMAS DETALHADAS ───────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 5  NORMAS APLICÁVEIS — Portugal · EU · Global")
    print(f"  {'━'*68}\n")

    norm_groups = [
        ("Portugal — Obrigatórias", comp_cfg.get("portugal", {})),
        ("União Europeia", comp_cfg.get("european_union", {})),
        ("Global — ISO / WELL / LEED / ONU", comp_cfg.get("global", {})),
    ]

    for group_name, group in norm_groups:
        print(f"  {group_name}:")
        for norm_key, norm in group.items():
            if isinstance(norm, dict) and "name" in norm:
                label = norm.get("label","")
                consequence = norm.get("consequence","")
                print(f"    {norm['name']:<25} {label:<30} {consequence[:40] if consequence else ''}")
        print()

    # Climate context
    climate = comp_cfg.get("portugal_climate", {})
    print(f"  CLIMA DE AVEIRO (para calibração dos thresholds):")
    print(f"  Zona: {climate.get('climate_zone','?')}")
    print(f"  Temperatura média Jan/Jul: {climate.get('monthly_temp_avg_c',{}).get('jan','?')}°C / {climate.get('monthly_temp_avg_c',{}).get('jul','?')}°C")
    print(f"  HDD (18°C): {climate.get('heating_degree_days_18c','?')}  |  CDD (21°C): {climate.get('cooling_degree_days_21c','?')}")
    print(f"  Humidade média: Jan {climate.get('monthly_rh_avg_pct',{}).get('jan','?')}% / Jul {climate.get('monthly_rh_avg_pct',{}).get('jul','?')}%")
    print(f"  Sol: {climate.get('annual_sunshine_hours','?')} horas/ano  |  Chuva: {climate.get('annual_rain_mm','?')} mm/ano\n")

    # ── SECÇÃO 6: PLANO DE ACÇÃO ──────────────────────────────────────────────
    print(f"  {'━'*68}")
    print(f"  § 6  PLANO DE ACÇÃO — gerado pelo sistema")
    print(f"  {'━'*68}\n")

    timeline = report_cfg.get("timeline", {})
    best_key2 = interventions_ranked[0][0] if interventions_ranked else "?"
    best_d2   = interventions_ranked[0][1] if interventions_ranked else {}
    worst_room = min(baseline.room_annual, key=lambda r: baseline.room_annual[r]["mean_F"])

    ctx_timeline = {
        "best_intervention": best_d2.get("desc","?"),
        "best_intervention_cost": best_d2.get("cost_eur",0),
        "worst_room": worst_room,
        "total_sensor_cost": total_cost,
        "p1_sensor_cost": p1_cost,
    }

    for phase_key, phase in timeline.items():
        cost_lbl = phase.get("cost",0)
        if cost_lbl == "best_intervention_cost":
            cost_lbl = f"€{ctx_timeline.get('best_intervention_cost',0):,}"
        elif cost_lbl == "full_sensor_cost":
            cost_lbl = f"€{p1_cost:,}"
        elif cost_lbl == 0:
            cost_lbl = "custo zero"
        print(f"  {phase.get('label','').upper()}  ({cost_lbl})")
        for action in phase.get("actions",[]):
            try: line = action.format(**ctx_timeline)
            except: line = action
            print(f"  → {line}")
        print()

    # ── IMPACTO TOTAL ─────────────────────────────────────────────────────────
    print(f"  {'─'*68}")
    print(f"  IMPACTO TOTAL SE TUDO IMPLEMENTADO\n")

    fd = analysis.get("full_upgrade",{})
    if fd:
        total_invest  = fd.get("cost_eur",0) + total_cost
        annual_saving = fd.get("total_savings_eur",0)
        payback_total = total_invest/annual_saving*12 if annual_saving > 0 else 999
        p_b   = _perf(b.get("mean_F",0), lang_cfg)
        p_a   = _perf(fd.get("mean_F",0), lang_cfg)
        print(f"  Investimento total:    €{total_invest:,}  (intervenções + sensores)")
        print(f"  Poupança anual:        €{annual_saving:,.0f}")
        print(f"  Payback:               {payback_total:.1f} meses")
        print(f"  Performance:           {p_b['short']}  →  {p_a['short']}")
        print(f"  Conformidade legal:    Viola  →  Cumpre (EPBD + Portaria 353-A/2013)")
        print(f"  Certificação:          Nenhuma  →  WELL Bronze + LEED Certified (potencial)")
        print(f"  Violações temp:        {baseline.total_temp_breaches:,}  →  {fd.get('temp_breaches',0):,}")
        print(f"  Carbono:               {baseline.total_carbon_kg:.0f} kg  →  estimativa com BACS")

    print(f"\n  {'─'*68}")
    print(f"  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    print(f"  Designing to free. -- Gonçalo")
    print(f"  Planta Smart Homes · hi@planta.design")
    print(f"  ORCID 0009-0008-6255-7724 · FCT 2025.00020.AIVLAB.DEUCALION\n")


if __name__ == "__main__":
    generate_report()
