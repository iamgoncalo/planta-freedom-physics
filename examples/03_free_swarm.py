#!/usr/bin/env python3
# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from freedom_physics.swarm.free_algorithm import run_FREE
rooms=[{"id":"A","P_spatial":0.8,"D_total":1.2,"capacity":20,"occupants":18},
       {"id":"B","P_spatial":0.6,"D_total":1.8,"capacity":15,"occupants":2},
       {"id":"C","P_spatial":0.5,"D_total":1.5,"capacity":12,"occupants":5},
       {"id":"Pintassilgo","P_spatial":0.3,"D_total":3.5,"capacity":12,"occupants":6}]
r=run_FREE(rooms,n_iter=100)
print(f"F_global: {r['F_global_before']} → {r['F_global_after']}")
print(f"Pintassilgo avoided: {'Pintassilgo' in r['avoided_rooms']}")
print("ALL RESULTS SIMULATION-BASED. seed=2026.")
