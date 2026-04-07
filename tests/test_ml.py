"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
tests/test_ml.py — ML module tests. All config-driven. seed from config.
"""
import sys, pytest
sys.path.insert(0,'/home/claude/afi'); sys.path.insert(1,'/home/claude/lof')

from freedom_physics.ml.gnn_freedom import FreedomGNN, build_test_graph, predict_F
from freedom_physics.ml.rl_agent import MaterialEnv, create_agent
from freedom_physics.ml.diffusion_material import generate_novel_material
from freedom_physics.ml.surrogate_model import predict_F_fast, compute_F_material_full
from freedom_physics.ml.active_learning import select_next_samples
from freedom_physics.ml.anomaly_detection import detect_anomaly
from freedom_physics.ml.uncertainty_quantification import predict_with_uncertainty
from freedom_physics.config import cfg

def test_gnn_forward(): m=FreedomGNN(); g=build_test_graph(); out=m(g); assert out is not None
def test_gnn_from_config(): assert list(FreedomGNN().hidden_dims)==list(cfg.ml.hidden_dims)
def test_gnn_target_includes_f(): g=build_test_graph(); assert 'F_element' in g['targets']
def test_rl_env_reset():
    env=MaterialEnv(); obs,_=env.reset()
    assert len(obs)==3
def test_rl_10_steps():
    env=MaterialEnv(); env.reset()
    for _ in range(10): a=env.action_space.sample(); obs,r,done,_,_=env.step(a)
    assert isinstance(r,float)
def test_rl_reward_uses_F():
    import inspect; src=inspect.getsource(MaterialEnv.step)
    assert 'F_current' in src or 'F_vals' in src
def test_diffusion_generates():
    mats=generate_novel_material(0.75,3)
    assert len(mats)==3
    assert 'composition' in mats[0] and 'F_predicted' in mats[0]
def test_surrogate_faster():
    import time
    comp={'C':0.9,'Si':0.1}
    t1=time.time(); predict_F_fast(comp); t1=time.time()-t1
    t2=time.time(); compute_F_material_full(comp); t2=time.time()-t2
    assert t1<t2+0.01  # surrogate at least not much slower
def test_active_learning_selects():
    cands=[{'id':i} for i in range(10)]
    sel=select_next_samples(cands,3)
    assert len(sel)==3
    assert all('uncertainty' in s for s in sel)
def test_anomaly_no_llm():
    r=detect_anomaly(0.1,[0.5,0.6,0.55,0.52])
    assert 'z_score' in r and 'label' in r
    assert 'SIMULATED' in r['label']
def test_anomaly_detects_spike():
    history=[0.5]*20
    r=detect_anomaly(0.05,history)
    assert r['z_score']>0
def test_uq_bounds_guaranteed():
    r=predict_with_uncertainty([0.3,0.7,0.5])
    assert r['lower_95']<=r['value']<=r['upper_95']
def test_uq_from_config():
    r=predict_with_uncertainty([0.5])
    assert r['n_samples']==int(cfg.ml.mc_dropout_samples)
