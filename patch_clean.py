"""
patch_clean.py — patch limpo após git checkout chat.py
Faz UMA coisa só: insere bio_run antes de TOOLS_DEF e regista-o.
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 patch_clean.py
"""
import os, ast

CHAT = os.path.expanduser("~/Downloads/planta-freedom-physics/chat.py")

with open(CHAT, "r") as f:
    src = f.read()

# Verifica sintaxe original
try:
    ast.parse(src)
    print("  ✓ chat.py original OK")
except SyntaxError as e:
    print(f"  ✗ chat.py está partido (linha {e.lineno}). Corre: git checkout chat.py")
    exit(1)

if "def bio_run(" in src:
    print("  ✓ bio_run já presente. Nada a fazer.")
    exit(0)

# ── 1. Inserir função bio_run antes de TOOLS_DEF ─────────────────────────────
BIO_FUNC = r'''
def bio_run(scenario="healthy"):
    """100 biological algorithms F=P/D. scenario: healthy|stress|fwh|lifecycle"""
    import importlib.util as _ilu, os as _os
    _dir = _os.path.dirname(_os.path.abspath(__file__))
    _path = _os.path.join(_dir, "bio_algorithms.py")
    if not _os.path.exists(_path):
        return {"error": "bio_algorithms.py not found in " + _dir}
    spec = _ilu.spec_from_file_location("bio_algorithms", _path)
    bio = _ilu.module_from_spec(spec); spec.loader.exec_module(bio)
    if scenario == "lifecycle":
        traj = bio.simulate_lifecycle(years=80)
        peak = max(traj, key=lambda t: t["F"])
        return {"years": len(traj), "peak_F": peak["F"], "peak_year": peak["year"],
                "mean_F": round(sum(t["F"] for t in traj)/len(traj), 4),
                "decades": [traj[min(i*10, len(traj)-1)]["F"] for i in range(9)],
                "label": "SIMULATED"}
    presets = {
        "healthy": bio.BioState(),
        "stress":  bio.BioState(co2_room_ppm=1100.0, core_temp_c=38.8,
                                fatigue_pct=75.0, pathogen_load=0.3, o2_sat_pct=93.0),
        "fwh":     bio.BioState(co2_room_ppm=420.0, atp_store_pct=90.0),
    }
    s = presets.get(scenario, bio.BioState())
    out = bio.run_all_algorithms(s, verbose=False)
    by_domain = {}
    for r in out["results"]:
        d = by_domain.setdefault(r.domain, {"active": [], "total": 0})
        d["total"] += 1
        if r.triggered:
            d["active"].append({"id": r.algo_id, "name": r.name,
                                "action": r.action[:100], "delta_F": r.delta_F})
    return {"scenario": scenario, "F_initial": out["F_initial"],
            "F_final": out["F_final"], "delta_F": out["delta_F"],
            "triggered": out["triggered"], "total": out["total"],
            "by_domain": by_domain,
            "house_bio_map": list(bio.HOUSE_BIO_MAP.items()),
            "label": "SIMULATED — F=P/D HYPOTHESIS UNDER TEST"}

'''

# Insere imediatamente antes de TOOLS_DEF
if "TOOLS_DEF" in src:
    src = src.replace("TOOLS_DEF", BIO_FUNC + "TOOLS_DEF", 1)
    print("  ✓ bio_run função inserida antes de TOOLS_DEF")
else:
    print("  ✗ TOOLS_DEF não encontrado"); exit(1)

# ── 2. Registar em TOOLS_DEF no formato correcto ─────────────────────────────
ENTRY = '    "bio_run":{"fn":bio_run,"desc":"Run all 100 biological algorithms D01-D10 F=P/D. Scenarios: healthy stress fwh lifecycle. Returns F, delta_F, all active algorithms, house-bio map.","params":{"scenario":"healthy | stress | fwh | lifecycle"}},\n'

idx = src.find('"simulate_physics":')
if idx != -1:
    line_start = src.rfind('\n', 0, idx) + 1
    src = src[:line_start] + ENTRY + src[line_start:]
    print("  ✓ bio_run registado em TOOLS_DEF")
else:
    print("  ✗ simulate_physics não encontrado"); exit(1)

# ── 3. Aumentar max_output_tokens ─────────────────────────────────────────────
import re
src, n = re.subn(r'max_output_tokens\s*=\s*\d+', 'max_output_tokens=8192', src)
if n: print(f"  ✓ max_output_tokens → 8192 ({n}×)")

# ── 4. Validar e guardar ──────────────────────────────────────────────────────
try:
    ast.parse(src)
    print("  ✓ Sintaxe OK")
    with open(CHAT, "w") as f:
        f.write(src)
    print(f"  ✓ GUARDADO\n")
    print("  Agora corre:")
    print("  export GEMINI_API_KEY=AIzaSyC5Xh0qckmb6UOwYSvGXXfZOgwZEfKNS9k")
    print("  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 ~/Downloads/planta-freedom-physics/chat.py")
    print()
    print("  Depois escreve:  run bio scenario healthy")
except SyntaxError as e:
    lines = src.splitlines()
    L = e.lineno - 1
    print(f"  ✗ Erro linha {e.lineno}: {e.msg}")
    for i in range(max(0,L-3), min(len(lines),L+4)):
        print(f"    {'>>>' if i==L else '   '} {i+1}: {lines[i]}")
    print("  NÃO GUARDADO.")
