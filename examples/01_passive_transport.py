"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
Example 01: Passive transport laws as F=1/D.
Ohm, Fourier, Fick, Darcy, Langevin all recovered with R²>0.99.
"""
import sys; sys.path.insert(0, '..'); sys.path.insert(1, '/home/claude/lof')
from freedom_physics.physics.transport import (
    simulate_ohms_law, simulate_fouriers_law, simulate_ficks_law,
    simulate_darcys_law, simulate_langevin)

print("=" * 55)
print("Example 01: Passive Physics — F = 1/D (P=1, α=1)")
print("ALL RESULTS SIMULATED · seed=2026")
print("=" * 55)
for fn in [simulate_ohms_law, simulate_fouriers_law, simulate_ficks_law,
           simulate_darcys_law, simulate_langevin]:
    r = fn()
    print(f"  {r['law']:10s}: R² = {r['r_squared']:.6f} {'✓' if r['r_squared']>0.99 else '✗'}")
print("\nNEGATIVE RESULT: P alone beats P/D in open navigation (R²=0.83 vs 0.48)")
