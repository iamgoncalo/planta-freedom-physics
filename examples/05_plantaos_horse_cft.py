#!/usr/bin/env python3
# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# Source: David Fleury HORSE Aveiro emails 3+12 Mar 2026
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from freedom_physics.buildings.plantaos_engine import compute_room_F, compute_building_F
rooms_data=[
    ("Hall_GF",      0.814,21,650,52,310,38,3, 10,0.5),
    ("Quintanilha",  0.246,28,750,65,280,46,14,15,2.1),
    ("Vasco_da_Gama",0.264,25,810,60,295,42,19,20,1.8),
    ("Pintassilgo",  0.385,24,690,58,85, 41,10,12,1.8),
]
rooms=[compute_room_F(r[0],*r[1:]) for r in rooms_data]
bldg=compute_building_F(rooms)
for r in rooms:
    flag=" ← EXCLUDED (no AC, 85 lux, HL-05)" if r['room_id']=="Pintassilgo" else ""
    print(f"  {r['room_id']:18s} F={r['F']:.4f} D={r['D_total']:.4f} alert={r['alert_level']}{flag}")
print(f"\nBuilding F_global={bldg['F_global']:.4f}  worst={bldg['worst_room']}")
print("ALL RESULTS SIMULATION-BASED. Source: David Fleury HORSE Aveiro.")
