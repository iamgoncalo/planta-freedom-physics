"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
tests/test_physics.py — Physics module tests. All 5 laws R²>0.99.
"""
import sys, math, pytest
sys.path.insert(0, '/home/claude/afi'); sys.path.insert(1, '/home/claude/lof')

from freedom_physics.physics.transport import (
    simulate_ohms_law, simulate_fouriers_law, simulate_ficks_law,
    simulate_darcys_law, simulate_langevin
)
from freedom_physics.physics.holographic import compute_F_volume_vs_boundary
from freedom_physics.physics.fine_tuning import scan_constant_space
from freedom_physics.physics.quantum_gravity import compute_F_by_dimension
from freedom_physics.core.constants_derivation import (
    derive_fine_structure_constant, derive_spacetime_dimensions, derive_cosmological_constant
)

def test_ohm_r2(): assert simulate_ohms_law()['r_squared'] > 0.99
def test_fourier_r2(): assert simulate_fouriers_law()['r_squared'] > 0.99
def test_fick_r2(): assert simulate_ficks_law()['r_squared'] > 0.99
def test_darcy_r2(): assert simulate_darcys_law()['r_squared'] > 0.99
def test_langevin_r2(): assert simulate_langevin()['r_squared'] > 0.99
def test_all_r2_label():
    for fn in [simulate_ohms_law, simulate_fouriers_law, simulate_ficks_law]:
        r = fn(); assert 'SIMULATED' in r['label']
def test_holographic_all_sizes():
    for sz in [2,4,8,16]:
        r = compute_F_volume_vs_boundary(sz)
        assert r['F_boundary'] > r['F_bulk'], f"Failed at size={sz}"
def test_fine_tuning_f_obs_above_mean():
    r = scan_constant_space()
    assert r['F_at_observed'] > r['F_random_mean']
    assert 'SIMULATED' in r['label']
def test_dimension_peak_at_3():
    dims = {n: compute_F_by_dimension(n) for n in range(1,8)}
    assert max(dims, key=lambda n: dims[n]) == 3
def test_alpha_structural_parallel():
    r = derive_fine_structure_constant()
    assert r['status'] == 'STRUCTURAL_PARALLEL'
    assert r['value_known'] == pytest.approx(1/137.036, rel=0.001)
def test_dimensions_derivation():
    r = derive_spacetime_dimensions()
    assert r['peak_at_N'] == 3
def test_cosmological_constant():
    r = derive_cosmological_constant()
    assert r['status'] in ['STRUCTURAL_PARALLEL','IRRECONCILABLE']
    assert 'SIMULATED' in r['label']
