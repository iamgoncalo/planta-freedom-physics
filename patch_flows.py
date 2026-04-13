"""
patch_flows.py — adiciona building_flows ao chat.py
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 patch_flows.py
"""
import os, ast

CHAT = os.path.expanduser("~/Downloads/planta-freedom-physics/chat.py")
with open(CHAT) as f: src = f.read()

try: ast.parse(src)
except SyntaxError as e:
    print(f"✗ chat.py partido ({e.lineno}). Corre: git checkout chat.py"); exit(1)

if "building_flows" in src:
    print("✓ building_flows já presente."); exit(0)

FUNC = '''
def tool_building_flows(scenario="morning_crisis", month=3, hour=9.0):
    """Flow intelligence: o edifício pensa em fluxos, não em dados. Scenario: morning_crisis|normal_day|evening|winter_cold|summer_heat"""
    import importlib.util, os as _os
    _dir = _os.path.dirname(_os.path.abspath(__file__))
    _path = _os.path.join(_dir, "building_flows.py")
    if not _os.path.exists(_path):
        return {"error": "building_flows.py not found"}
    spec = importlib.util.spec_from_file_location("building_flows", _path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.tool_building_flows(str(scenario), int(month), float(hour))

'''

ENTRY = '    "building_flows":{"fn":tool_building_flows,"desc":"Flow intelligence engine for HORSE CFT. Thinks in flows not data points. Scenarios: morning_crisis, normal_day, evening, winter_cold, summer_heat. Returns plain Portuguese narrative, emergencies, systemic problems, F score, active flows.","params":{"scenario":"morning_crisis|normal_day|evening|winter_cold|summer_heat","month":"1-12","hour":"0-24"}},\n'

src = src.replace("TOOLS_DEF", FUNC + "TOOLS_DEF", 1)

idx = src.find('"bio_run":')
if idx == -1: idx = src.find('"simulate_physics":')
line_start = src.rfind('\n', 0, idx) + 1
src = src[:line_start] + ENTRY + src[line_start:]

try:
    ast.parse(src)
    with open(CHAT, "w") as f: f.write(src)
    print("✓ building_flows integrado no chat.py")
    print("\nCorre:")
    print("export GEMINI_API_KEY=AIzaSyC5Xh0qckmb6UOwYSvGXXfZOgwZEfKNS9k")
    print("/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 ~/Downloads/planta-freedom-physics/chat.py")
    print("\nPergunta:")
    print("  simulate building morning crisis scenario")
    print("  what is happening in the building right now?")
    print("  show building flows winter cold")
except SyntaxError as e:
    lines = src.splitlines()
    L = e.lineno - 1
    print(f"✗ Erro {e.lineno}: {e.msg}")
    for i in range(max(0,L-3),min(len(lines),L+4)):
        print(f"  {'>>>' if i==L else '   '} {i+1}: {lines[i]}")
    print("NOT saved.")
