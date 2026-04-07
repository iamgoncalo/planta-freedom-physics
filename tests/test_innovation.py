"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
tests/test_innovation.py — Innovation module tests.
"""
import sys, pytest
sys.path.insert(0, '.'); 

from freedom_physics.innovation.innovation_scorer import score_innovation, full_innovation_report
from freedom_physics.chemistry.creation_sequence import get_all_stages, get_stellar_F_nuclear, get_stage_by_element
from freedom_physics.chemistry.bonding import bond_freedom, bond_d_hierarchy
from freedom_physics.chemistry.reactions import reaction_direction, reaction_free_energy

def test_innovation_score_range():
    for F,n in [(0.3,0.5),(0.7,0.8),(1.0,1.0),(0.0,0.0)]:
        assert 0<=score_innovation(F,n)<=1
def test_innovation_full_report():
    r=full_innovation_report({'C':0.5,'Si':0.3,'Al':0.2},0.64)
    assert 'F_innovation' in r and 'suggested_claim' in r
    assert 'SIMULATED' in r['label']
def test_creation_12_stages(): assert len(get_all_stages())>=12
def test_creation_vacuum():
    stages=get_all_stages()
    assert any('vacuum' in s['name'].lower() for s in stages)
def test_creation_iron():
    stages=get_all_stages()
    assert any('iron' in s['name'].lower() for s in stages)
def test_creation_rprocess():
    stages=get_all_stages()
    assert any('r-process' in s['name'].lower() or 'neutron' in s['name'].lower() for s in stages)
def test_stellar_F_nuclear():
    seq=get_stellar_F_nuclear()
    assert 26 in seq
    fe_f=seq[26]; assert fe_f>0.99
def test_stage_by_element(): s=get_stage_by_element(26); assert 'iron' in s['name'].lower()
def test_bond_freedom_range():
    for bond in ['H-H','C-C','N≡N']:
        r=bond_freedom(bond); assert 0<=r['F_bond']<=1
def test_bond_stronger_lower_F():
    weak=bond_freedom('Fe-Fe'); strong=bond_freedom('N≡N')
    assert strong['D_bond_kJ_mol'] > weak['D_bond_kJ_mol']
def test_bond_hierarchy_sorted():
    h=bond_d_hierarchy(); assert h[0]['D_bond_kJ_mol']>=h[-1]['D_bond_kJ_mol']
def test_reaction_spontaneous(): r=reaction_direction(0.3,0.7); assert r['spontaneous']==True
def test_reaction_nonspontaneous(): r=reaction_direction(0.8,0.4); assert r['spontaneous']==False
def test_reaction_gibbs():
    r=reaction_free_energy(-100,298,50); assert r['spontaneous']==True and r['delta_G_J']<0
