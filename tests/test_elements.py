# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
import sys, os, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, '/home/claude/lof')
from freedom_physics.chemistry.periodic_table import PERIODIC_TABLE, freedom_of, most_free

def test_118_elements():          assert len(PERIODIC_TABLE)==118
def test_noble_gas_chem_zero():
    for s in ["He","Ne","Ar","Kr","Xe","Rn"]:
        assert PERIODIC_TABLE[s].F_chemical()==0.0,f"{s} F_chem must be 0"
def test_iron_top5_nuclear():     assert "Fe" in [e["symbol"] for e in most_free("nuclear",5)]
def test_silver_max_electrical(): assert PERIODIC_TABLE["Ag"].F_electrical()>=0.99
def test_H_high_chemical():       assert PERIODIC_TABLE["H"].F_chemical()>0.40
def test_Fe_nuclear_gt_U():       assert PERIODIC_TABLE["Fe"].F_nuclear()>PERIODIC_TABLE["U"].F_nuclear()
def test_freedom_of():            assert 0.9<freedom_of("Cu","electrical")<1.01
def test_all_F_in_01():
    for sym in list(PERIODIC_TABLE.keys())[:20]:
        for ch in ["electrical","thermal","chemical","nuclear"]:
            F=freedom_of(sym,ch); assert 0<=F<=1,f"{sym} {ch} F={F}"
