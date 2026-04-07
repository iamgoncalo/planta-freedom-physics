# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

physics/thermodynamics.py — Thermodynamics as F=P/D. T2+T4.
Second law: D increases spontaneously (Freedom decreases).
Boltzmann: S=k*ln(W) where W=Freedom measure of system.
"""
from __future__ import annotations
import math
from freedom_physics.config import get_epsilon

def boltzmann_freedom(T_K: float, E_barrier_J: float) -> dict:
    "F=kT/E_barrier (P=kT, D=E_barrier). Probability ~ exp(-E/kT). T2."
    from scipy import constants
    k_B=constants.k; eps=get_epsilon()
    P=k_B*T_K; D=max(E_barrier_J,eps)
    F=P/D
    prob=math.exp(-E_barrier_J/max(k_B*T_K,eps))
    return {"F":round(F,6),"P_thermal":P,"D_barrier":D,"boltzmann_factor":round(prob,6),
            "law":"p~exp(-E/kT)=exp(-D/P_therm)","thesis":"T2","label":"SIMULATED"}

def carnot_freedom(T_cold: float, T_hot: float) -> dict:
    "F=eta=1-Tc/Th. T2."
    eps=get_epsilon()
    D=T_cold/max(T_hot,eps)
    eta=max(0.0,1.0-D)
    return {"F_efficiency":round(eta,6),"D_thermal_ratio":round(D,6),
            "T_cold_K":T_cold,"T_hot_K":T_hot,"law":"eta=1-Tc/Th","thesis":"T2","label":"SIMULATED"}

def entropy_as_D_measure(microstates: int) -> dict:
    "S=k*ln(W). W=number of accessible microstates=F-measure. T2+T5."
    from scipy import constants
    k_B=constants.k; eps=get_epsilon()
    S=k_B*math.log(max(microstates,1))
    F_measure=math.log(max(microstates,1))
    return {"entropy_S_J_per_K":S,"F_measure_ln_W":round(F_measure,4),
            "microstates":microstates,"law":"S=k*ln(W)","thesis":"T2+T5","label":"SIMULATED"}

def second_law_direction(D_initial: float, D_final: float) -> dict:
    "Second law: D increases spontaneously. Freedom decreases. T5."
    spontaneous=(D_final>=D_initial)
    return {"D_initial":D_initial,"D_final":D_final,"D_increased":spontaneous,
            "F_decreased":spontaneous,"spontaneous":spontaneous,
            "law":"D increases spontaneously (Second Law = T5)","thesis":"T5","label":"SIMULATED"}