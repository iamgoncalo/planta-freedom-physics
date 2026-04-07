"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
tests/test_toe_derivations.py — TOE derivation engine tests.
Primary: planta_toe_100.py (100-criterion, zero hardcodes).
Legacy: derive_all.py (50-criterion).
"""
import sys, math, pytest
sys.path.insert(0, '.'); 
from freedom_physics.config import cfg

# 100-criterion engine
from freedom_physics.toe.planta_toe_100 import run_all_100
_R100 = run_all_100()
_BY100 = {d["id"]: d for d in _R100["results"]}

def test_score_100(): assert _R100["score"] == 100.0
def test_all_100_derived(): assert _R100["n_DERIVED"] == 100
def test_zero_errors(): assert _R100["n_errors"] == 0
def test_100_criteria(): assert len(_R100["results"]) == 100
def test_all_have_proof():
    for d in _R100["results"]:
        assert d.get("proof","").strip(), f"C{d['id']} missing proof"
def test_all_thesis_traces():
    for d in _R100["results"]:
        trace = d.get("thesis_trace","")
        assert any(f"T{n}" in trace for n in range(1,6)), f"C{d['id']} missing T-trace"
def test_all_labeled():
    for d in _R100["results"]:
        assert "SIMULATED" in d.get("label",""), f"C{d['id']} missing SIMULATED"

def test_C013_ohm_r2():  assert _BY100[13]["r_squared"] > 0.99
def test_C026_bell():    assert _BY100[26]["F_quantum"] > _BY100[26]["F_classical"]
def test_C048_mass_ratio():
    assert abs(_BY100[48]["ratio_AFI"] - 1836.12) < 0.01
    assert _BY100[48]["error_pct"] < 0.01
def test_C047_bohr_exact(): assert _BY100[47]["error_pct"] < 1e-3
def test_C034_lambda():     assert _BY100[34]["error_pct"] < 2.0
def test_C091_godel():      assert _BY100[91]["godel_supports_AFI"]
def test_C007_asymmetry():
    assert _BY100[7]["dominant_r2_deucalion"] == float(cfg.perception.level2_r2_dominant)
def test_C008_structural():
    assert _BY100[8]["r2_structural_deucalion"] == float(cfg.perception.level25_r2)
    assert _BY100[8]["rho_L1_vs_L25_deucalion"] < 0
def test_C009_l_gap():
    assert _BY100[9]["dead_formula"]["r2"] == float(cfg.perception.dead_r2)

# Legacy 50-criterion
from freedom_physics.toe.derive_all import run_all_derivations
_R50 = run_all_derivations()
_BY50 = {d["criterion"]: d for d in _R50["derivations"]}
def test_50_score(): assert _R50["score_out_of_50"] == 50.0
def test_50_derived(): assert _R50["n_DERIVED"] == 50
def test_50_godel():       assert _BY50[50]["godel_supports_AFI"]
def test_50_mass_ratio():  assert _BY50[19]["error_pct"] < 0.01
def test_50_lambda_err():  assert _BY50[20]["error_pct"] < 2.0
def test_50_cosmological(): assert _BY50[29]["F_initial"] > 0.99
