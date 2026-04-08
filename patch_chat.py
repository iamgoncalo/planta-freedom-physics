#!/usr/bin/env python3
"""
patch_chat.py — fixes all tool bugs in chat.py in place.
Run: python3 patch_chat.py
"""
import os, sys, ast

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat.py')
if not os.path.exists(TARGET):
    print(f"ERROR: {TARGET} not found"); sys.exit(1)

content = open(TARGET).read()
patches = 0

def patch_fn(content, fn_name, new_body):
    start = content.find(f"\ndef {fn_name}(")
    if start == -1:
        start = content.find(f"def {fn_name}(")
        if start == -1: print(f"  SKIP  {fn_name}"); return content, False
    else: start += 1
    end = content.find("\ndef ", start + 10)
    if end == -1: end = len(content)
    content = content[:start] + new_body.strip() + "\n\n" + content[end:]
    print(f"  PATCH {fn_name}")
    return content, True

# 1. find_best_elements — real mendeleev data, short output
content, ok = patch_fn(content, "tool_find_best_elements", '''
def tool_find_best_elements(use_case: str = "combined", n: int = 10,
                             max_price: float = 1000.0, min_F: float = 0.0) -> str:
    use_case = str(use_case or "combined").strip().lower()
    try: n = int(float(str(n).strip() or "10"))
    except: n = 10
    try: max_price = float(str(max_price).strip() or "1000.0")
    except: max_price = 1000.0
    results = []
    for z in range(1, 119):
        try:
            el = mend_element(z); d = _F_element(el)
            if not d: continue
            price = float(d.get("price_per_kg_eur") or 50.0)
            if price > max_price: continue
            score = {"structural":d.get("F_structural",0),"thermal":d.get("F_thermal",0),
                "chemical":d.get("F_chemical",0),"cost":d.get("F_cost",0),
                "combined":d.get("F_total",0),"building":d.get("F_building",0),
                "electronics":d.get("F_electronics",0),"aerospace":d.get("F_aerospace",0),
                "smart_brick":d.get("F_smart_brick",0),"coastal":d.get("F_coastal",0),
                "nuclear":d.get("F_nuclear",0),"water_home":d.get("F_water_home",0),
            }.get(use_case, d.get("F_total", 0))
            results.append({"rank":0,"symbol":d["symbol"],"name":d["name"],
                "F_score":round(float(score),4),"F_total":round(float(d.get("F_total",0)),4),
                "F_building":round(float(d.get("F_building",0)),4),
                "F_water_home":round(float(d.get("F_water_home",0)),4),
                "density":d.get("density_g_cm3",0),"melting_K":d.get("melting_point_K",0),
                "price_eur_kg":round(price,2),"lattice":d.get("lattice","?")})
        except Exception: continue
    results.sort(key=lambda x: x["F_score"], reverse=True)
    top = results[:n]
    for i,r in enumerate(top,1): r["rank"] = i
    summary = " | ".join(f"{r['symbol']}={r['F_score']}" for r in top[:5])
    return json.dumps({"use_case":use_case,"n_analysed":118,"n_shown":len(top),
        "top5_summary":summary,"top_elements":top,"label":LABEL}, default=str)
''')
if ok: patches += 1

# 2. temporal_simulation — keyword args + stats only (no trajectory dump)
content, ok = patch_fn(content, "tool_temporal_simulation", '''
def tool_temporal_simulation(n_agents: int = 4, duration_min: float = 60.0,
                              ACH: float = 6.0, room_volume_m3: float = 75.0) -> str:
    if not _GAPS_OK: return json.dumps({"error": "afi_gaps.py not loaded"})
    try:
        na  = int(float(str(n_agents).strip()   or "4"))
        dm  = float(str(duration_min).strip()   or "60.0")
        ach = float(str(ACH).strip()            or "6.0")
        vol = float(str(room_volume_m3).strip() or "75.0")
        result = simulate_temporal_feedback(n_agents=na, duration_min=dm, ACH=ach, room_volume_m3=vol)
        stats = result.get("statistics", {})
        traj  = result.get("trajectory", [])
        alert_mins   = [t["t_min"] for t in traj if t.get("alert_level",0) >= 2]
        breach_mins  = [t["t_min"] for t in traj if t.get("CO2_ppm",0) >= 1000]
        return json.dumps({
            "params": {"n_agents":na,"duration_min":dm,"ACH":ach,"vol_m3":vol},
            "F_mean":round(float(stats.get("F_mean",0)),4),
            "F_min": round(float(stats.get("F_min",0)),4),
            "F_max": round(float(stats.get("F_max",0)),4),
            "CO2_peak_ppm":  stats.get("CO2_peak_ppm"),
            "CO2_ss_ppm":    stats.get("CO2_ss_ppm"),
            "CO2_tau_min":   stats.get("CO2_tau_min"),
            "n_alerts":      stats.get("n_alerts"),
            "f_debt_eur":    stats.get("total_f_debt_eur"),
            "first_alert_min":       alert_mins[0] if alert_mins else None,
            "first_CO2_breach_min":  breach_mins[0] if breach_mins else None,
            "equations":     result.get("equations",{}),
            "label": LABEL,
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "ACH": str(ACH)})
''')
if ok: patches += 1

# 3. compute_room_F **kwargs — only if not already present
if 'def tool_compute_room_F' in content:
    sig_start = content.find('def tool_compute_room_F')
    sig_end   = content.find(':', sig_start) + 1
    sig_block = content[sig_start:sig_end]
    if '**kwargs' not in sig_block:
        fixed = sig_block.rstrip()
        if fixed.endswith('):'):
            fixed = fixed[:-2] + ', **kwargs):'
        content = content[:sig_start] + fixed + content[sig_start+len(sig_block):]
        print("  PATCH compute_room_F **kwargs"); patches += 1
    else:
        print("  SKIP  compute_room_F **kwargs already present")

# 4. banner + system prompt v5
for old,new in [('Physical AI v4.0','Physical AI v5.0'),
                ('PHYSICAL AI  v4.0','PHYSICAL AI  v5.0')]:
    if old in content:
        content = content.replace(old, new)
        print(f"  PATCH {old} -> {new}"); patches += 1

# 5. Anti-hallucination rule
old_r = '11. NEVER invent numbers. NEVER hardcode. All values from tools only.'
new_r = ('11. NEVER invent numbers. NEVER hardcode. ALL values from tools only.\n'
         '    CRITICAL: After tool call, use ONLY numbers from JSON result.\n'
         '    The #1 element is top_elements[0].symbol and top_elements[0].F_score.\n'
         '    NEVER write Carbon=0.985 or Tungsten=0.972 — those are hallucinated.\n'
         '    Report EXACTLY: "Rank 1: {symbol} F={F_score}" from tool output.')
if old_r in content:
    content = content.replace(old_r, new_r)
    print("  PATCH anti-hallucination rule"); patches += 1

# Validate
try: ast.parse(content)
except SyntaxError as e:
    print(f"\nSYNTAX ERROR line {e.lineno}: {e.msg}"); sys.exit(1)

open(TARGET,'w').write(content)
print(f"\nDONE — {patches} patches applied")
