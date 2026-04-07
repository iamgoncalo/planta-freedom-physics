"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
Example 05: THE FLAGSHIP — Build a house with C, Si, Al.
10-step Freedom Physics pipeline.
"""
import sys; sys.path.insert(0, '..'); sys.path.insert(1, '/home/claude/lof')
from freedom_physics.structures.house_designer import design_house

print("=" * 60)
print("Example 05: House Designer — C + Si + Al")
print("Input: 80m² · €10,000 budget · structural priority")
print("ALL RESULTS SIMULATED · F=P/D HYPOTHESIS UNDER TEST")
print("=" * 60)

r = design_house(["C","Si","Al"], area_m2=80, budget_eur=10000)
comp  = r["step2_pso"]["best_composition"]
mat   = r["step3_material"]
struc = r["step4_structure"]
cost  = r["step5_cost"]
innov = r["step6_innovation"]
econ  = r["step7_economics"]

print(f"\nStep 2 — PSO Composition:")
for e, f in comp.items(): print(f"  {e}: {f:.1%}")
print(f"\nStep 3 — Material: F_composite = {mat['F_composite']}")
print(f"  E_modulus_GPa = {mat.get('E_modulus_GPa','?')}")
print(f"  F_thermal     = {mat['F_thermal']}")
print(f"\nStep 4 — Structure: F_global = {struc['F_global']}")
print(f"  Members: {struc['n_members']} · Weak: {len(struc['weak_members'])}")
print(f"  Safety OK: {struc['safety_ok']}")
print(f"\nStep 5 — Cost: €{cost['total_eur']:,.0f}")
print(f"  Within budget: {cost['within_budget']} (budget: €{cost['budget_eur']:,.0f})")
print(f"\nStep 6 — Innovation: F_innovation = {innov['F_innovation']}")
print(f"  Novel: {innov['novel']}")
print(f"\nStep 7 — F-debt avoided: €{econ['F_debt_avoided_eur_yr']:,.0f}/year")
print(f"\n{r['label']}")
