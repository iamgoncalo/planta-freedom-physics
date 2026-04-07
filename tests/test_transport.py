# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
import sys,os,math,pytest
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np; from scipy.stats import pearsonr

def test_ohm_recovery():
    "F=1/R. R²>0.99. Test with R>1 so clip doesn't mask the relationship."
    from freedom_physics.core.freedom import compute_F_passive
    rng=np.random.default_rng(2026)
    R=rng.uniform(1.0,100,500)  # R>1 only so F<1 always (no clipping)
    F=[compute_F_passive(r) for r in R]
    F_exp=[1/r for r in R]
    r,_=pearsonr(F,F_exp); assert r**2>0.99,f"Ohm R²={r**2:.4f}"

def test_tunneling():
    from freedom_physics.physics.quantum import tunneling_freedom
    rng=np.random.default_rng(2026)
    kv=rng.uniform(0.1,5,100); Lv=rng.uniform(0.1,3,100)
    F=[tunneling_freedom(k,L)["F"] for k,L in zip(kv,Lv)]
    Fe=[math.exp(-2*k*L) for k,L in zip(kv,Lv)]
    r,_=pearsonr(F,Fe); assert r**2>0.99,f"Tunneling R²={r**2:.4f}"

def test_planck_unity():
    from freedom_physics.physics.quantum import planck_scale_unity
    r=planck_scale_unity(); assert abs(r["ratio_D_Q_D_G"]-1.0)<0.01

def test_dead_formula():
    from freedom_physics.core.perception import p_dead_log2NT
    with pytest.raises(RuntimeError): p_dead_log2NT(10,0.5)

def test_carnot():
    from freedom_physics.physics.thermodynamics import carnot_freedom
    r=carnot_freedom(300,600); assert abs(r["F_efficiency"]-0.5)<0.001

def test_D_geometric_differs_from_additive():
    "Geometric and additive D are different when channels differ."
    from freedom_physics.core.distortion import distortion_geometric
    rng=np.random.default_rng(2026)
    # Use clearly different channel values
    ch=[{"a":rng.uniform(1,5),"b":rng.uniform(5,10)} for _ in range(50)]
    w={"a":0.5,"b":0.5}
    D_g=[distortion_geometric(c,w)[0] for c in ch]
    D_a=[0.5*c["a"]+0.5*c["b"] for c in ch]
    diffs=[abs(g-a) for g,a in zip(D_g,D_a)]
    assert sum(d>0.01 for d in diffs)>45,"Geometric must usually differ from additive"
