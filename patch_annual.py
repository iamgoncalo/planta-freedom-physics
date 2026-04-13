"""
patch_annual.py
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 patch_annual.py
"""
import os, ast

CHAT = os.path.expanduser("~/Downloads/planta-freedom-physics/chat.py")
with open(CHAT) as f: src = f.read()
try: ast.parse(src)
except SyntaxError as e: print(f"✗ chat.py partido ({e.lineno}). git checkout chat.py"); exit(1)
if "annual_simulation" in src: print("✓ já presente."); exit(0)

FUNC = '''
def tool_annual_simulation(mode="baseline", intervention="none"):
    """Full year HORSE CFT simulation. mode: baseline|intervention|compare_all. intervention: none|pintassilgo_fix|cantina_hvac|all_halls|full_upgrade"""
    import importlib.util, os as _os
    _dir = _os.path.dirname(_os.path.abspath(__file__))
    _path = _os.path.join(_dir, "annual_simulation.py")
    if not _os.path.exists(_path):
        return {"error": "annual_simulation.py not found in " + _dir}
    spec = importlib.util.spec_from_file_location("annual_simulation", _path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.tool_annual_simulation(str(mode), str(intervention))

'''

ENTRY = '    "annual_simulation":{"fn":tool_annual_simulation,"desc":"Full year building simulation for HORSE CFT. Simulates all 365 operating days, every room, every hour. Shows F score, F-debt in EUR, CO2 legal breaches, temperature violations, energy kWh, worst and best hours of the year, and ROI of interventions. mode: baseline|intervention|compare_all. intervention: none|pintassilgo_fix|cantina_hvac|all_halls|full_upgrade","params":{"mode":"baseline|intervention|compare_all","intervention":"none|pintassilgo_fix|cantina_hvac|all_halls|full_upgrade"}},\n'

src = src.replace("TOOLS_DEF", FUNC + "TOOLS_DEF", 1)
idx = src.find('"building_flows":')
if idx == -1: idx = src.find('"bio_run":')
line_start = src.rfind('\n', 0, idx) + 1
src = src[:line_start] + ENTRY + src[line_start:]

try:
    ast.parse(src)
    with open(CHAT, "w") as f: f.write(src)
    print("✓ annual_simulation integrado no chat.py\n")
    print("Perguntas para o chat:")
    print('  simulate the full year baseline')
    print('  compare all interventions and show ROI')
    print('  what happens if we fix pintassilgo?')
    print('  what was the worst day of the year?')
    print('  show the full upgrade impact')
except SyntaxError as e:
    lines = src.splitlines()
    L = e.lineno-1
    print(f"✗ {e.lineno}: {e.msg}")
    for i in range(max(0,L-2),min(len(lines),L+3)):
        print(f"  {'>>>' if i==L else '   '} {i+1}: {lines[i]}")
    print("NOT saved.")
