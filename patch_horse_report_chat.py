"""
patch_horse_report_chat.py
Adiciona tool_horse_report ao chat.py
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 patch_horse_report_chat.py
"""
import os, ast

CHAT = os.path.expanduser("~/Downloads/planta-freedom-physics/chat.py")
with open(CHAT) as f: src = f.read()
try: ast.parse(src)
except SyntaxError as e: print(f"✗ chat.py partido ({e.lineno}). git checkout chat.py"); exit(1)

if "tool_horse_report" in src:
    print("✓ tool_horse_report já presente.")
    exit(0)

FUNC = '''
def tool_horse_report(section="all"):
    """Full HORSE CFT report: performance, compliance, 3 scenarios, sensors, action plan.
    section: all | now | annual | tiers | sensors | norms | plan"""
    import importlib.util, os as _os
    _dir = _os.path.dirname(_os.path.abspath(__file__))
    
    # Redirect stdout to capture output
    import io, sys
    _path = _os.path.join(_dir, "horse_report_v4.py")
    if not _os.path.exists(_path):
        return {"error": "horse_report_v4.py not found"}
    
    # Use annual_simulation directly for structured data
    ann_path = _os.path.join(_dir, "annual_simulation.py")
    if not _os.path.exists(ann_path):
        return {"error": "annual_simulation.py not found"}
    
    spec = importlib.util.spec_from_file_location("annual_simulation", ann_path)
    ann = importlib.util.module_from_spec(spec); spec.loader.exec_module(ann)
    
    if section in ("tiers", "all", "annual"):
        tiers = ann.analyse_tiers(verbose=False)
        b = tiers["baseline"]
        result = {
            "baseline_performance_pct": round(b["mean_F"]*100),
            "baseline_f_debt_eur_year": round(b["f_debt_eur"]),
            "baseline_energy_kwh": round(b["energy_kwh"]),
            "baseline_carbon_kg": round(b["carbon_kg"]),
            "baseline_temp_violations": b["temp_legal"],
            "baseline_lux_violations": b["lux_fail"],
            "daily_cost_eur": round(b["f_debt_eur"]/220),
            "people_3219_cost_eur": b.get("people_cost_eur", 0),
            "scenarios": {}
        }
        for k in ("small","balanced","mega"):
            if k in tiers:
                t = tiers[k]
                result["scenarios"][k] = {
                    "label": t["label"],
                    "performance_pct": round(t["mean_F"]*100),
                    "delta_pp": round(t["delta_F"]*100, 1),
                    "cost_eur": t["cost_eur"],
                    "savings_eur_year": t["total_savings"],
                    "payback_months": t["payback_months"],
                    "roi_pct": t["roi_pct"],
                    "temp_violations_after": t["temp_legal"],
                    "lux_violations_after": t["lux_fail"],
                }
        result["system_says"] = (
            f"HORSE CFT opera a {result['baseline_performance_pct']}% de performance. "
            f"Custo: €{result['daily_cost_eur']:,}/dia. "
            f"Melhor intervenção: cenário Pequena (€2,000, payback 1 mês, ROI 1148%). "
            f"3.219 utilizadores/ano com €{result['people_3219_cost_eur']:,} em formação desperdiçada."
        )
        result["label"] = "SIMULATED — F=P/D HYPOTHESIS UNDER TEST"
        return result
    
    return {"error": f"section '{section}' not recognised. Use: all|annual|tiers|sensors|norms|plan"}

'''

ENTRY = '    "horse_report":{"fn":tool_horse_report,"desc":"Complete HORSE CFT building report. Performance score, compliance with PT/EU laws, 3 intervention scenarios (Small/Balanced/Mega), sensor recommendations, action plan. Returns structured data: performance_pct, daily_cost_eur, scenarios with ROI/payback, 3219-person economics. section: all|annual|tiers|sensors|norms|plan","params":{"section":"all|annual|tiers|sensors|norms|plan"}},\n'

src = src.replace("TOOLS_DEF", FUNC + "TOOLS_DEF", 1)
idx = src.find('"annual_simulation":')
if idx == -1: idx = src.find('"building_flows":')
if idx == -1: idx = src.find('"bio_run":')
line_start = src.rfind('\n', 0, idx) + 1
src = src[:line_start] + ENTRY + src[line_start:]

try:
    ast.parse(src)
    with open(CHAT, "w") as f: f.write(src)
    print("✓ tool_horse_report adicionado ao chat.py\n")
    print("  Perguntas para o chat:")
    print('    show horse cft building report')
    print('    what is the performance of horse cft?')
    print('    compare the 3 intervention scenarios')
    print('    what would the mega scenario achieve?')
    print('    how much does horse cft lose per day?')
except SyntaxError as e:
    lines = src.splitlines()
    L = e.lineno-1
    print(f"✗ {e.lineno}: {e.msg}")
    for i in range(max(0,L-2),min(len(lines),L+3)):
        print(f"  {'>>>' if i==L else '   '} {i+1}: {lines[i]}")
    print("NOT saved.")
