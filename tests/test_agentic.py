"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
tests/test_agentic.py — Agentic module tests.
"""
import sys, pytest
sys.path.insert(0,'/home/claude/afi'); sys.path.insert(1,'/home/claude/lof')

from freedom_physics.agentic.query_parser import parse_query
from freedom_physics.agentic.result_narrator import narrate_result
from freedom_physics.agentic.session_manager import SessionManager
from freedom_physics.agentic.voice_interface import VoiceInterface
from freedom_physics.agentic.physics_agent import explain_physics
from freedom_physics.agentic.building_agent import simulate_scenario
from freedom_physics.agentic.innovation_agent import assess_novelty
from freedom_physics.agentic.material_agent import build_from_query
from freedom_physics.config import cfg

def test_parse_house_en(): r=parse_query("Build me a house with C, Si, Al"); assert r['intent']=='house_design'
def test_parse_elements(): r=parse_query("Build with Carbon and Silicon"); assert 'C' in r['elements']
def test_parse_area(): r=parse_query("house 80m2"); assert r['area_m2']==80.0
def test_parse_physics(): r=parse_query("Why does Ohm law work?"); assert r['intent']=='physics_explanation'
def test_parse_innovation(): r=parse_query("Is this novel and patentable?"); assert r['intent']=='innovation_assessment'
def test_narrator_en():
    t=narrate_result({'F_composite':0.7,'cost_eur':8500},'en')
    assert len(t)>20 and 'SIMULATED' in t
def test_narrator_pt():
    t=narrate_result({'F_composite':0.7,'cost_eur':8500},'pt')
    assert 'score' in t.lower() or 'resultado' in t.lower() or 'freedom' in t.lower()
def test_narrator_max_words():
    t=narrate_result({'F_composite':0.7,'cost_eur':8500},'en')
    assert len(t.split()) <= int(cfg.voice.max_response_words)
def test_session_cost_limits():
    sm=SessionManager()
    assert sm.cost_limit_day==float(cfg.ai_agents.cost_limit_day_eur)
    assert sm.cost_limit_month==float(cfg.ai_agents.cost_limit_month_eur)
def test_session_caching():
    sm=SessionManager()
    r1=sm.get_cached_or_call("test",mock=True)
    r2=sm.get_cached_or_call("test",mock=True)
    assert r1==r2
def test_session_state():
    sm=SessionManager(); sm.save_state("key","val"); assert sm.get_state("key")=="val"
def test_voice_mock_init(): vi=VoiceInterface(mock=True); assert vi.mock==True
def test_voice_stt_mock(): vi=VoiceInterface(mock=True); assert isinstance(vi.stt_mock("x"),str)
def test_voice_tts_mock(): vi=VoiceInterface(mock=True); assert isinstance(vi.tts_mock("hi"),bytes)
def test_physics_ohm(): r=explain_physics("Ohm's law from AFI"); assert 'T2' in r['thesis_trace']
def test_physics_iron(): r=explain_physics("Why does iron stop stars?"); assert 'Fe' in r['explanation']
def test_physics_has_steps(): r=explain_physics("Ohm"); assert len(r['derivation_steps'])>=3
def test_building_heatwave():
    r=simulate_scenario('heatwave',4)
    assert len(r['F_global_t'])==4*60
    assert r['F_global_end']<r['F_global_start']
def test_innovation_range():
    r=assess_novelty({'C':0.5,'Si':0.3,'Al':0.2})
    assert 0<=r['novelty_score']<=1
def test_innovation_prior_art(): r=assess_novelty({'C':0.5,'Si':0.5}); assert 'prior_art' in r
def test_material_agent_runs():
    parsed={'elements':['C','Si','Al'],'area_m2':80,'budget_eur':10000,'priority':'structural'}
    r=build_from_query(parsed)
    assert 'step4_structure' in r
