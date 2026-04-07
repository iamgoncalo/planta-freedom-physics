#!/usr/bin/env python3
# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from freedom_physics.elements.periodic_table import PERIODIC_TABLE, freedom_of, most_free
print(f"Total elements: {len(PERIODIC_TABLE)}/118")
print("\nTop 5 nuclear freedom:")
for e in most_free("nuclear",5): print(f"  {e['symbol']:3s}: {e['F']:.4f}")
print("\nNoble gases F_chemical=0:")
for s in ["He","Ne","Ar","Kr","Xe","Rn"]:
    f=PERIODIC_TABLE[s].F_chemical()
    print(f"  {s}: {f:.4f} {'✓' if f==0 else 'FAIL'}")
print(f"\nFe F_nuclear={freedom_of('Fe','nuclear'):.4f}  Ag F_electrical={freedom_of('Ag','electrical'):.4f}")
print("ALL RESULTS SIMULATION-BASED. seed=2026.")
