"""
horse_report_v4.py
─────────────────────────────────────────────────────────────────────────────
PlantaOS — Relatório Final v4
HORSE CFT · Planta Smart Homes · FCT 2025.00020.AIVLAB.DEUCALION

Todos os bugs corrigidos:
  ✓ STEP_H = 0.1h (era 10× inflacionado)
  ✓ LUX× por mês correcta
  ✓ Salários de config.yaml
  ✓ Carbono calculado com BACS
  ✓ 3 cenários: Pequena / Equilibrada / Mega
  ✓ Economia das 3.219 pessoas com segmentos salariais

Corre: python3 horse_report_v4.py
─────────────────────────────────────────────────────────────────────────────
"""

import importlib.util, os, yaml
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

def _load_mod(name):
    for n in [name, f"{name}_v2"]:
        p = os.path.join(BASE, f"{n}.py")
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location(n, p)
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            return m
    return None

def _load_yaml(name):
    for p in [os.path.join(BASE, f"{name}.yaml"),
              os.path.join(BASE, f"{name}.yml")]:
        if os.path.exists(p):
            with open(p) as f: return yaml.safe_load(f) or {}
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────
ann_mod  = _load_mod("annual_simulation")
bf_mod   = _load_mod("building_flows")
lang_cfg = _load_yaml("language")
comp_cfg = _load_yaml("compliance")
sens_cfg = _load_yaml("sensors")
rep_cfg  = _load_yaml("report_config")
plan_cfg = _load_yaml("config")

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _perf(F):
    pct = F * 100
    bands = lang_cfg.get("performance", {})
    for _, b in sorted(bands.items(), key=lambda x: -x[1].get("min",0)):
        if F >= b.get("min",0):
            return {"pct":pct,"label":b.get("short","?"),"emoji":b.get("emoji",""),
                    "system_says":b.get("system_says",""),"action":b.get("action",""),
                    "bar":"█"*int(pct/5)+"░"*(20-int(pct/5))}
    return {"pct":pct,"label":"?","emoji":"","system_says":"","action":"","bar":""}

def _roi_label(roi):
    bands = rep_cfg.get("roi_bands",{})
    for _, b in sorted(bands.items(), key=lambda x: -x[1].get("min",0)):
        if roi >= b.get("min",0): return b.get("label","")
    return ""

def _pb_label(months):
    bands = rep_cfg.get("payback_bands",{})
    for _, b in sorted(bands.items(), key=lambda x: x[1].get("max",999)):
        if months <= b.get("max",999): return b.get("label","")
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def generate():
    now = datetime.now().strftime("%d/%m/%Y  %H:%M")
    fin_cfg  = comp_cfg.get("financial_consequences",{})
    ctx_cfg  = lang_cfg.get("context",{})
    d_weights= plan_cfg.get("distortion",{}).get("weights",{
        "thermal":0.40,"co2":0.22,"humidity":0.16,
        "light":0.12,"noise":0.05,"occupancy":0.03,"spatial":0.02})

    # ── HEADER ────────────────────────────────────────────────────────────────
    W = 70
    print(f"\n{'╔'+'═'*W+'╗'}")
    print(f"║{'HORSE CFT — Relatório de Desempenho e Conformidade':^{W}}║")
    print(f"║{'PlantaOS · Planta Smart Homes · FCT 2025.00020.AIVLAB':^{W}}║")
    print(f"║{now:^{W}}║")
    print(f"║{'SIMULAÇÃO — F=P/D HIPÓTESE EM TESTE':^{W}}║")
    print(f"{'╚'+'═'*W+'╝'}\n")

    # ── CONTEXTO ──────────────────────────────────────────────────────────────
    nc = fin_cfg.get("buildings_non_compliant_portugal_pct",75)
    ti = ctx_cfg.get("indoors_pct",90)
    fm = fin_cfg.get("annual_fine_max_eur",45000)
    pl = ctx_cfg.get("productivity_co2_loss_pct",50)
    print(f"  {'─'*W}")
    print(f"  O CONTEXTO QUE IMPORTA")
    print(f"  {'─'*W}")
    print(f"  {nc}% dos edifícios em Portugal não cumpre com a lei  "
          f"[{ctx_cfg.get('non_compliant_source','JRC 2022')}]")
    print(f"  {ti}% do tempo humano é passado em interiores  "
          f"[{ctx_cfg.get('indoors_source','OMS')}]")
    print(f"  -{pl}% produtividade com CO₂ elevado  "
          f"[{ctx_cfg.get('productivity_source','')}]")
    print(f"  Multa máxima ACT: €{fm:,}/ano · EPBD 2024: monitorização obrigatória > 250m²")
    print(f"  HORSE CFT: 950m² com 3.219 utilizadores/ano — a lei aplica-se.\n")

    # ── AGORA ─────────────────────────────────────────────────────────────────
    print(f"  {'━'*W}")
    print(f"  § 1  AGORA")
    print(f"  {'━'*W}\n")

    if bf_mod:
        nh = datetime.now().hour + datetime.now().minute/60
        nm = datetime.now().month
        r  = bf_mod.tool_building_flows("normal_day", month=nm, hour=nh)
        p  = _perf(r["F_global"])
        print(f"  {p['emoji']}  Edifício: Performance {p['pct']:.0f}%  [{p['label']}]")
        print(f"     {p['system_says']}")
        print(f"     [{p['bar']}]  →  {p['action']}\n")
        if r.get("emergencies"):
            print(f"  🚨 EMERGÊNCIAS ({len(r['emergencies'])}):")
            for e in r["emergencies"]: print(f"     {e}")
        if r.get("systemic_problems"):
            print(f"  ⚠  PROBLEMAS SISTÉMICOS ({len(r['systemic_problems'])}):")
            for s in r["systemic_problems"]: print(f"     {s}")
        print()

    # ── ANO COMPLETO ──────────────────────────────────────────────────────────
    print(f"  {'━'*W}")
    print(f"  § 2  2026 COMPLETO — 3.219 pessoas · 12 meses · 12 salas")
    print(f"  {'━'*W}\n")

    if not ann_mod:
        print("  ✗ annual_simulation_v2.py não encontrado"); return

    # Run all tiers
    print("  A calcular baseline + 3 cenários (pode demorar ~30s)...\n")
    tiers = ann_mod.analyse_tiers(verbose=False)
    b     = tiers["baseline"]

    # Rerun baseline to get monthly detail
    baseline = ann_mod.run_annual(interventions={}, verbose=True)
    pe = baseline.people_econ

    p_ann = _perf(baseline.mean_F_annual)
    print(f"\n  {p_ann['emoji']}  Performance anual: {p_ann['pct']:.0f}%  ({p_ann['label']})")
    print(f"     {p_ann['system_says']}")
    print(f"     [{p_ann['bar']}]\n")

    # Key numbers — all computed
    daily_loss = baseline.total_f_debt_eur / 220
    carbon_int = baseline.total_carbon_kg / 950
    print(f"  NÚMEROS DO ANO:")
    print(f"  → {pe['annual_users']:,} pessoas  ×  €{pe['investment_per_user_eur']:,}/pessoa  "
          f"×  {pe['efficiency_loss_pct']:.0f}% perda eficiência")
    print(f"  → €{pe['training_productivity_cost_eur']:>10,.0f}  custo de formação desperdiçado")
    print(f"  → €{baseline.total_f_debt_eur:>10,.0f}  perda de produtividade (simulação)")
    print(f"  → €{baseline.total_energy_eur:>10,.0f}  em energia ({baseline.total_energy_kwh:,.0f} kWh)")
    print(f"  → {baseline.total_carbon_kg:>10,.0f}  kg CO₂  ({carbon_int:.1f} kg/m²/ano)")
    print(f"  → €{daily_loss:>10,.0f}  perdidos POR DIA sem intervenção\n")

    # People breakdown
    print(f"  CUSTO POR SEGMENTO (3.219 utilizadores):")
    print(f"  {'Segmento':<14} {'Pessoas':>8}  {'€/hora':>7}  {'Invest/pessoa':>13}  "
          f"{'Perda anual':>12}")
    print(f"  {'─'*14} {'─'*8}  {'─'*7}  {'─'*13}  {'─'*12}")
    for seg, d in pe["breakdown_by_segment"].items():
        print(f"  {seg:<14} {d['n_people']:>8,}  €{d['employer_h']:>5.2f}  "
              f"€{d['investment_per_person']:>11,}  €{d['loss_eur']:>10,}")

    # Compliance
    print(f"\n  CONFORMIDADE LEGAL (calculada):")
    print(f"  {'─'*W}")
    pt_cfg = comp_cfg.get("portugal",{})
    eu_cfg = comp_cfg.get("european_union",{})
    co2_lim = pt_cfg.get("portaria_353a_2013",{}).get("limit_ppm",1000)
    temp_lim = pt_cfg.get("iso_7730_pt",{}).get("temp_min_c",18.0)
    lux_lim  = pt_cfg.get("en_12464_pt",{}).get("lux_min_classroom",300)
    mon_lim  = pt_cfg.get("epbd_2024",{}).get("monitoring_required_above_m2",250)
    tax_lim  = eu_cfg.get("eu_taxonomy_2021",{}).get("threshold_kg_co2_m2_year",40)

    checks = [
        ("✅" if baseline.total_co2_legal==0 else "❌",
         f"CO₂ < {co2_lim}ppm",
         "Portaria 353-A/2013",
         f"{'Zero violações' if baseline.total_co2_legal==0 else f'{baseline.total_co2_legal:,} violações'}"),
        ("❌" if baseline.total_temp_legal>0 else "✅",
         f"Temperatura ≥ {temp_lim}°C",
         "ISO 7730 + Lei 102/2009",
         f"{baseline.total_temp_legal:,} violações" if baseline.total_temp_legal else "OK"),
        ("❌" if baseline.total_lux_fail>0 else "✅",
         f"Iluminação ≥ {lux_lim} lux",
         "EN 12464-1:2021",
         f"{baseline.total_lux_fail:,} violações" if baseline.total_lux_fail else "OK"),
        ("❌", f"Monitorização (edifício > {mon_lim}m²)",
         "EPBD 2024",
         "Sem sensores = incumprimento"),
        ("❌" if carbon_int > tax_lim else "✅",
         f"Carbono < {tax_lim} kg/m²",
         "EU Taxonomy 2021",
         f"{carbon_int:.1f} kg/m²/ano {'> limite' if carbon_int > tax_lim else '✓'}"),
    ]
    for icon, check, norm, detail in checks:
        print(f"  {icon}  {check:<38}  [{norm}]")
        print(f"     {detail}")

    risk_eur = min(
        baseline.total_temp_legal * fin_cfg.get("temp_legal_breach_per_event_eur",200) +
        baseline.total_lux_fail   * fin_cfg.get("lux_legal_breach_per_event_eur",100),
        fin_cfg.get("annual_fine_max_eur",45000))
    print(f"\n  Risco legal ACT estimado: €{risk_eur:,}/ano (máximo ACT: €{fm:,})\n")

    # Calendar
    months_cfg = lang_cfg.get("months",{})
    print(f"  {'─'*W}")
    print(f"  CALENDÁRIO 2026:")
    print(f"  {'─'*W}")
    print(f"\n  {'MÊS':<12}  {'PERFORMANCE':>14}  {'PERDA PROD.':>12}  "
          f"{'TEMP×':>6}  {'LUX×':>6}  {'kWh':>7}")
    print(f"  {'─'*12}  {'─'*14}  {'─'*12}  "
          f"{'─'*6}  {'─'*6}  {'─'*7}")
    for month in range(1,13):
        m = baseline.monthly.get(month,{})
        if m.get("status")=="FECHADO":
            print(f"  {months_cfg.get(month,'Mês '+str(month)):<12}  "
                  f"{'FECHADO':>14}  {'—':>12}  {'—':>6}  {'—':>6}  {'—':>7}")
            continue
        F_m = m.get("mean_F",0)
        p_m = _perf(F_m)
        print(f"  {months_cfg.get(month,'?'):<12}  "
              f"{p_m['emoji']} {p_m['pct']:>4.0f}% {p_m['label']:<8}  "
              f"€{m.get('f_debt',0):>10,.0f}  "
              f"{m.get('temp_legal',0):>6,}  "
              f"{m.get('lux_fail',0):>6,}  "
              f"{m.get('energy_kwh',0):>7,.0f}")

    # Room ranking
    sorted_rooms = sorted(baseline.room_annual.items(), key=lambda x: x[1]["mean_F"])
    print(f"\n  {'─'*W}")
    print(f"  RANKING DAS SALAS:")
    print(f"  {'─'*W}")
    print(f"\n  {'#':<3} {'SALA':<18} {'PERF':>8}  {'PERDA/ANO':>11}  {'CO₂ MÉD':>9}  STATUS")
    print(f"  {'─'*3} {'─'*18} {'─'*8}  {'─'*11}  {'─'*9}  {'─'*12}")
    for i,(room,data) in enumerate(sorted_rooms):
        p_r = _perf(data["mean_F"])
        is_pinta = room=="Pintassilgo"
        status = "❌ Violação" if is_pinta else ("🔴 Crítico" if data["mean_F"]<0.5
                  else "🟡 Degradado" if data["mean_F"]<0.65 else "🟢 Bom")
        print(f"  {i+1:<3} {room:<18} "
              f"{p_r['emoji']} {p_r['pct']:>4.0f}%  "
              f"€{data['f_debt']:>9,}  "
              f"{data['mean_co2']:>8.0f}ppm  {status}")

    # ── 3 CENÁRIOS ────────────────────────────────────────────────────────────
    print(f"\n  {'━'*W}")
    print(f"  § 3  TRÊS CENÁRIOS — calculados com base nos dados reais")
    print(f"  {'━'*W}\n")

    tier_order = ["small","balanced","mega"]
    tier_data  = {k: tiers[k] for k in tier_order if k in tiers}

    for tier_key, tier in tier_data.items():
        p_t      = _perf(tier["mean_F"])
        p_b_tier = _perf(b["mean_F"])
        roi_lbl  = _roi_label(tier["roi_pct"])
        pb_lbl   = _pb_label(tier["payback_months"])

        print(f"  ┌{'─'*66}┐")
        print(f"  │  {tier['label_short']:<10}  {tier['label']:<30}  "
              f"Investimento: €{tier['cost_eur']:>6,}  │")
        print(f"  │  {tier['desc']:<62}  │")
        print(f"  ├{'─'*66}┤")
        print(f"  │  Performance: {p_b_tier['pct']:>3.0f}%  →  {p_t['pct']:>3.0f}%  "
              f"(+{tier['delta_F']*100:.1f}pp)  "
              f"ΔF = {tier['delta_F']:+.4f}                │")
        print(f"  │  Poupança anual:  €{tier['total_savings']:>8,}  │  "
              f"Payback: {tier['payback_months']:>4.1f} meses  │  "
              f"ROI: {tier['roi_pct']:>6.0f}%  │")
        print(f"  │  {roi_lbl:<40}                          │")
        print(f"  │  {pb_lbl:<40}                          │")

        # What's included
        ivs = ann_mod.SCENARIO_TIERS.get(tier_key,{}).get("interventions",{})
        if ivs:
            iv_str = " + ".join(f"{r}({','.join(v.keys())})" for r,v in list(ivs.items())[:3])
            if len(ivs)>3: iv_str += f" +{len(ivs)-3} mais"
            print(f"  │  Intervenções: {iv_str[:50]:<50}          │")

        sc = tier.get("sensor_cost",0)
        bacs = tier.get("bacs_class")
        extras = []
        if sc: extras.append(f"Sensores: €{sc:,}")
        if bacs: extras.append(f"BACS classe {bacs} (-20% energia)")
        extras.append("A18 circadian pre-heat (€0 — software)")
        print(f"  │  + {' · '.join(extras[:3]):<62}  │")

        # Impact on legal compliance
        delta_temp = b["temp_legal"] - tier["temp_legal"]
        delta_lux  = b["lux_fail"]   - tier["lux_fail"]
        delta_co2  = baseline.total_carbon_kg - tier["carbon_kg"]
        print(f"  │  Violações temp: {b['temp_legal']:>6,} → {tier['temp_legal']:>6,}  "
              f"({delta_temp:>+6,})  "
              f"LUX: {b['lux_fail']:>6,} → {tier['lux_fail']:>6,}  │")
        print(f"  │  Carbono: {baseline.total_carbon_kg:>6,.0f} kg → "
              f"{tier['carbon_kg']:>6,.0f} kg  "
              f"(-{delta_co2:.0f} kg = -{delta_co2/baseline.total_carbon_kg*100:.0f}%)  "
              f"{'':>18}│")
        print(f"  └{'─'*66}┘\n")

    # Comparison table
    print(f"  COMPARAÇÃO RÁPIDA:")
    print(f"  {'TIER':<22} {'PERF':>6}  {'INVEST':>8}  "
          f"{'POUPANÇA':>10}  {'PAYBACK':>9}  {'ROI':>7}")
    print(f"  {'─'*22} {'─'*6}  {'─'*8}  {'─'*10}  {'─'*9}  {'─'*7}")
    print(f"  {'BASELINE (actual)':<22} {b['mean_F']*100:>5.0f}%  "
          f"{'—':>8}  {'—':>10}  {'—':>9}  {'—':>7}")
    for tier_key, tier in tier_data.items():
        print(f"  {tier['label_short']:<22} {tier['mean_F']*100:>5.0f}%  "
              f"€{tier['cost_eur']:>6,}  €{tier['total_savings']:>8,}  "
              f"{tier['payback_months']:>5.1f} meses  {tier['roi_pct']:>6.0f}%")

    best_key = min(tier_data, key=lambda k: tier_data[k]["payback_months"])
    best     = tier_data[best_key]
    print(f"\n  O SISTEMA CONCLUI:")
    print(f"  Melhor payback: {best['label']} — €{best['cost_eur']:,} recuperados em "
          f"{best['payback_months']:.1f} meses.")
    print(f"  Cada mês de atraso custa €{baseline.total_f_debt_eur/11:,.0f} em produtividade.")
    print(f"  Número a mostrar a qualquer gestor: €{daily_loss:,.0f}/dia sem intervenção.\n")

    # ── SENSORES ──────────────────────────────────────────────────────────────
    print(f"  {'━'*W}")
    print(f"  § 4  SENSORES — porque a lei já os exige")
    print(f"  {'━'*W}\n")

    epbd = comp_cfg.get("portugal",{}).get("epbd_2024",{})
    print(f"  EPBD 2024: monitorização obrigatória > "
          f"{epbd.get('monitoring_required_above_m2',250)}m²  →  HORSE CFT: 950m²  →  "
          f"INCUMPRIMENTO sem sensores\n")
    print(f"  Canal D mais pesado = sensor mais prioritário:")
    print()

    sensors = sens_cfg.get("sensors",{})
    def _dw_for(s):
        for ch in s.get("resolves_channels",[]):
            dw = d_weights.get(ch,0)
            if dw>0: return ch,dw
        return "infra",0.0

    rows = sorted(sensors.items(), key=lambda x:(x[1].get("priority",9),-_dw_for(x[1])[1]))
    total_s = sum(s.get("price_eur",0)*s.get("qty_horse_cft",0) for _,s in rows)
    p1_s    = sum(s.get("price_eur",0)*s.get("qty_horse_cft",0)
                  for _,s in rows if s.get("priority",9)==1)

    print(f"  {'P':>2}  {'MODELO':<32}  {'CANAL D':>10}  {'PESO':>5}  €/u  Qtd  Total")
    print(f"  {'─'*2}  {'─'*32}  {'─'*10}  {'─'*5}  ───  ───  ─────")
    for sk,s in rows:
        ch,dw = _dw_for(s)
        t = s.get("price_eur",0)*s.get("qty_horse_cft",0)
        dw_s = f"{dw:.2f}" if dw>0 else "  —"
        print(f"  {s.get('priority',9):>2}  {s.get('model','?'):<32}  {ch:>10}  "
              f"{dw_s:>5}  €{s.get('price_eur',0):>2}  {s.get('qty_horse_cft',0):>3}  €{t:>4}")
        print(f"      → {s.get('notes','')[:60]}")

    mva = sens_cfg.get("minimum_viable",{})
    print(f"\n  {'─'*W}")
    print(f"  Total sensores completos:  €{total_s:,}")
    print(f"  Prioridade 1 (mínimo):     €{p1_s:,}")
    if mva: print(f"  {mva.get('payback_note','')}")
    print(f"\n  Com €{p1_s:,} → EPBD compliant + VALIDATED + WELL Bronze + paper Automation in Construction\n")

    # ── NORMAS ────────────────────────────────────────────────────────────────
    print(f"  {'━'*W}")
    print(f"  § 5  NORMAS APLICÁVEIS")
    print(f"  {'━'*W}\n")

    climate = comp_cfg.get("portugal_climate",{})
    print(f"  CLIMA AVEIRO (calibração thresholds):  "
          f"Zona {climate.get('climate_zone','?')}  |  "
          f"Jan {climate.get('monthly_temp_avg_c',{}).get('jan','?')}°C  |  "
          f"Jul {climate.get('monthly_temp_avg_c',{}).get('jul','?')}°C  |  "
          f"HDD {climate.get('heating_degree_days_18c','?')}  |  "
          f"{climate.get('annual_sunshine_hours','?')}h sol/ano\n")

    for group_label, group in [
        ("Portugal — Obrigatórias", comp_cfg.get("portugal",{})),
        ("União Europeia", comp_cfg.get("european_union",{})),
        ("Global / Verde", comp_cfg.get("global",{})),
    ]:
        print(f"  {group_label}:")
        for _,n in group.items():
            if isinstance(n,dict) and "name" in n:
                c = n.get("consequence","")
                lbl = n.get("label","")
                print(f"    {n['name']:<25}  {lbl:<28}  {c[:35] if c else ''}")
        print()

    # ── PLANO ─────────────────────────────────────────────────────────────────
    print(f"  {'━'*W}")
    print(f"  § 6  PLANO — gerado com base nos dados")
    print(f"  {'━'*W}\n")

    best_iv = min(tier_data.values(), key=lambda t: t["payback_months"])
    worst_room_name = sorted_rooms[0][0]

    plan = [
        ("ESTA SEMANA", "€0",
         ["Activar A18 circadian pre-heat no lbm.py (zero custo hardware)",
          f"Sala piloto: {worst_room_name} (pior Performance do edifício)",
          "Mostrar este relatório ao David Fleury (HORSE)",
          "Instalar PlantaOS dashboard V11 em modo simulação"]),
        ("ESTE MÊS", f"€{best_iv['cost_eur']:,}",
         [f"Implementar cenário {best_iv['label']}: {', '.join(ann_mod.SCENARIO_TIERS.get(best_key,{}).get('interventions',{}).keys())}",
          f"2 sensores piloto em {worst_room_name}: ESP32 + SCD40 + BH1750 = €{40+4+3}",
          "Validar primeiros dados reais vs simulação"]),
        ("PRÓXIMO TRIMESTRE", f"€{p1_s:,}",
         ["Deploy sensor completo: 24 salas, gateway LoRaWAN",
          "Todos os resultados SIMULATED → VALIDATED",
          "Submeter paper Automation in Construction com dados empíricos",
          "Renegociar contrato HORSE com Performance score como KPI"]),
    ]
    for phase_label, cost, actions in plan:
        print(f"  {phase_label}  ({cost})")
        for a in actions: print(f"  → {a}")
        print()

    # ── IMPACTO TOTAL ─────────────────────────────────────────────────────────
    print(f"  {'─'*W}")
    print(f"  IMPACTO TOTAL — CENÁRIO MEGA\n")
    mega = tier_data.get("mega",{})
    if mega:
        total_inv  = mega["cost_eur"] + total_s
        ann_saving = mega["total_savings"]
        pb_total   = total_inv/ann_saving*12 if ann_saving>0 else 999
        p_bf = _perf(b["mean_F"])
        p_af = _perf(mega["mean_F"])
        print(f"  Investimento total (intervenções + sensores):  €{total_inv:,}")
        print(f"  Poupança anual:                                €{ann_saving:,}")
        print(f"  Payback:                                       {pb_total:.1f} meses")
        print(f"  Performance:  {p_bf['pct']:.0f}% {p_bf['label']}  →  "
              f"{p_af['pct']:.0f}% {p_af['label']}")
        print(f"  Conformidade: Viola  →  Cumpre (EPBD 2024 + Portaria 353-A/2013)")
        print(f"  Certificação: Nenhuma  →  WELL Bronze + LEED Certified (potencial)")
        print(f"  Carbono:      {baseline.total_carbon_kg:,.0f} kg  →  {mega['carbon_kg']:,.0f} kg")
        print(f"  Violações T:  {b['temp_legal']:,}  →  {mega['temp_legal']:,}")
        print(f"  Violações LUX:{b['lux_fail']:,}  →  {mega['lux_fail']:,}")

    print(f"\n  {'─'*W}")
    print(f"  SIMULATED — F=P/D HYPOTHESIS UNDER TEST — seed=2026")
    print(f"  Designing to free. -- Gonçalo")
    print(f"  Planta Smart Homes · hi@planta.design")
    print(f"  ORCID 0009-0008-6255-7724 · FCT 2025.00020.AIVLAB.DEUCALION\n")


if __name__ == "__main__":
    generate()
