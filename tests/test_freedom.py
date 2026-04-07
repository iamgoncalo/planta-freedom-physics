# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
import sys, os, math, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freedom_physics.core.freedom import (
    compute_F, compute_F_passive, compute_F_global, verify_axioms)
from freedom_physics.core.distortion import distortion_geometric
from freedom_physics.config import get_building_weights, get_atomic_weights, get_seed

def test_F_basic():                   assert abs(compute_F(1.0,1.0)-1.0)<1e-9
def test_F_halved_by_double_D():      assert abs(compute_F(1.0,2.0)-0.5)<1e-9
def test_F_passive_P1():              assert compute_F_passive(1.0)==1.0 and compute_F_passive(2.0)==0.5
def test_F_global_geometric():
    import math
    vals=[0.4,0.6,0.8]
    exp=math.exp(sum(math.log(v) for v in vals)/3)
    assert abs(compute_F_global(vals)-exp)<1e-9
def test_axiom_C1():                  assert verify_axioms(0.5,2.0)["C1_monotonicity"] is True
def test_axiom_C2():                  assert verify_axioms(0.5,2.0)["C2_scale_covariance"] is True
def test_building_weights_1():        assert abs(sum(get_building_weights().values())-1.0)<1e-6
def test_atomic_weights_1():          assert abs(sum(get_atomic_weights().values())-1.0)<1e-6
def test_geometric_not_additive():
    D,_=distortion_geometric({"a":2.0,"b":3.0},{"a":0.5,"b":0.5})
    assert abs(D-math.sqrt(6))<1e-9 and D!=2.5
def test_D_weights_enforced():
    with pytest.raises(AssertionError): distortion_geometric({"a":1.0},{"a":0.99})
def test_seed_2026():                 assert get_seed()==2026
def test_F_clips_01():                assert compute_F(100.,0.001)==1.0 and compute_F(0.,100.)==0.0
