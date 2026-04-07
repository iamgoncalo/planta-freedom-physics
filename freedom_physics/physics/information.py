# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

physics/information.py — Information theory as F=P/D. T2+T5.
Shannon, channel capacity, Bekenstein bound as structural parallels.
"""
from __future__ import annotations
import math
from freedom_physics.config import get_epsilon

def channel_capacity_freedom(signal: float, noise: float, bandwidth_Hz: float) -> dict:
    "C=B*log(1+S/N). F=P/D where P=signal, D=noise. T2."
    eps=get_epsilon()
    D=max(noise,eps); P=max(signal,0.0)
    SNR=P/D
    C=bandwidth_Hz*math.log2(1+SNR)
    F=SNR/(1+SNR)
    return {"F_channel":round(F,6),"P_signal":P,"D_noise":D,"SNR":round(SNR,4),
            "capacity_bits_s":round(C,2),"law":"C=B*log2(1+S/N)","thesis":"T2","label":"SIMULATED"}

def bekenstein_entropy(M_kg: float) -> dict:
    "S=A/4l_P². Boundary D accumulation. T2+T5."
    from scipy import constants
    hbar=constants.hbar; G=constants.G; c=constants.c
    r_s=2*G*M_kg/c**2
    l_P=math.sqrt(hbar*G/c**3)
    A=4*math.pi*r_s**2
    S=A/(4*l_P**2)
    return {"S_over_kB":S,"area_m2":A,"r_s_m":r_s,
            "interpretation":"S=A/4l_P² = boundary D accumulation. Holographic.",
            "thesis":"T2+T5","label":"SIMULATED"}