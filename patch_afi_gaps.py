#!/usr/bin/env python3
"""
patch_afi_gaps.py — fixes divide-by-zero when ACH=0 in afi_gaps.py
Run: python3 patch_afi_gaps.py
"""
import os, sys, ast

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'afi_gaps.py')
if not os.path.exists(TARGET):
    print(f"ERROR: {TARGET} not found"); sys.exit(1)

content = open(TARGET).read()

# Fix 1: divide by zero in co2_tau
old1 = 'co2_tau = room_volume_m3 / Q_vent / 60.0'
new1 = 'co2_tau = (room_volume_m3 / Q_vent / 60.0) if Q_vent > 1e-9 else float("inf")'
if old1 in content:
    content = content.replace(old1, new1)
    print("PATCH 1: co2_tau divide-by-zero fixed")
else:
    print("SKIP  1: already patched or not found")

# Fix 2: dCO2_dt when Q_vent=0 — sealed room keeps accumulating
old2 = "        C_frac   = C * 1e-6\n        dC_dt    = (n * g_CO2_per_person - Q_vent * (C_frac - C_outdoor)) / room_volume_m3"
new2 = "        C_frac   = C * 1e-6\n        if Q_vent < 1e-9:  # sealed room — pure accumulation\n            dC_dt = n * g_CO2_per_person / room_volume_m3\n        else:\n            dC_dt = (n * g_CO2_per_person - Q_vent * (C_frac - C_outdoor)) / room_volume_m3"
if old2 in content:
    content = content.replace(old2, new2)
    print("PATCH 2: sealed room CO2 accumulation fixed")
else:
    print("SKIP  2: already patched or not found")

# Fix 3: dT_dt when Q_vent=0
old3 = "        Q_loss   = U_fabric * A_fabric * max(0, T_K - T_outdoor_K)\n        dT_dt    = (Q_in - Q_loss) / (m_air * Cp_air)"
new3 = "        Q_loss   = U_fabric * A_fabric * max(0, T_K - T_outdoor_K)\n        Q_vent_loss = Q_vent * rho_air * Cp_air * max(0, T_K - T_outdoor_K) if Q_vent > 1e-9 else 0.0\n        dT_dt    = (Q_in - Q_loss - Q_vent_loss) / (m_air * Cp_air)"
if old3 in content:
    content = content.replace(old3, new3)
    print("PATCH 3: sealed room thermal model fixed")
else:
    print("SKIP  3: already patched or not found")

try:
    ast.parse(content)
except SyntaxError as e:
    print(f"\nSYNTAX ERROR line {e.lineno}: {e.msg}"); sys.exit(1)

open(TARGET,'w').write(content)
print("\nDONE — afi_gaps.py patched")

# Quick test
import sys
sys.path.insert(0, os.path.dirname(TARGET))
import importlib
import afi_gaps
importlib.reload(afi_gaps)
result = afi_gaps.simulate_temporal_feedback(n_agents=1, duration_min=480, ACH=0.0, room_volume_m3=20.0)
stats = result['statistics']
traj  = result.get('trajectory',[])
breach = [t['t_min'] for t in traj if t.get('CO2_ppm',0)>=1000]
print(f"\nTEST: 1 person sealed room 8h")
print(f"  CO2 peak: {stats['CO2_peak_ppm']} ppm")
print(f"  First breach >1000ppm: {breach[0] if breach else 'None'} min")
print(f"  F_mean: {stats['F_mean']}, F_min: {stats['F_min']}")
print(f"  Alerts: {stats['n_alerts']}")
