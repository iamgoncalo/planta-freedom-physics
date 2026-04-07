# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"""
import math, numpy as np

_EPS = 1.0e-14

def freedom(P, D, alpha=1.0, clip=True):
    D_s = np.maximum(np.asarray(D, dtype=float), _EPS)
    F   = (np.asarray(P, dtype=float) / D_s) ** alpha
    if clip: F = np.clip(F, 0.0, 1.0)
    return float(F) if np.asarray(F).ndim == 0 else F

def freedom_rate(P, D, P_dot, D_dot):
    return (P_dot*max(D,_EPS) - P*D_dot) / max(D,_EPS)**2

def verify_axioms(P, D, delta=0.01):
    F0   = freedom(P, D, clip=False)
    dFdP = (freedom(P+delta,D,clip=False)-freedom(P-delta,D,clip=False))/(2*delta)
    dFdD = (freedom(P,D+delta,clip=False)-freedom(P,D-delta,clip=False))/(2*delta)
    c1 = dFdP>0 and dFdD<0
    c2 = all(abs(freedom(l*P,l*D,clip=False)-F0)<1e-9 for l in [0.1,2.0,100.0])
    return {"C1":c1,"C2":c2,"F":F0,"all_pass":c1 and c2}
