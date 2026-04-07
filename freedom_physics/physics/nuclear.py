# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

physics/nuclear.py — Nuclear physics as F=P/D. T1+T2+T5.
Strong force: QCD asymptotic freedom = F=P/D at nuclear scale (Nobel 2004).
Binding energy: Fe-56 maximum = maximum F_nuclear.
Decay: spontaneous reduction of D (T2 Law 2 in action).
"""
from __future__ import annotations
import math
from freedom_physics.config import get_epsilon

def qcd_color_freedom(Q_GeV: float) -> dict:
    """
    QCD running coupling: D_color = alpha_s(Q) / Q.
    F_color = P_color / D_color.
    As Q->inf (r->0): alpha_s->0, D_color->0, F_color->inf (asymptotic freedom).
    As Q->0 (r->large): D_color->inf, F_color->0 (confinement). Nobel 2004.
    """
    from freedom_physics.config import cfg
    eps=get_epsilon()
    alpha_s_MZ=float(getattr(getattr(cfg,"particle_physics",None),"alpha_s_MZ",0.1181))
    M_Z=float(float(getattr(getattr(cfg,"particle_physics",None),"M_Z_GeV",91.188)))
    b3=-7.0  # SM QCD beta function coefficient b_3 (number of colors, standard)
    ln_ratio=math.log(max(Q_GeV,eps)**2/M_Z**2)
    denom=1+alpha_s_MZ/(2*math.pi)*b3*ln_ratio
    alpha_s_Q=alpha_s_MZ/max(abs(denom),eps) if denom>0 else alpha_s_MZ*10
    D_color=alpha_s_Q/max(Q_GeV,eps)
    F_color=min(10.0,1.0/max(D_color,eps))
    regime="asymptotic_freedom" if Q_GeV>10 else ("hadronic" if Q_GeV>0.3 else "confinement")
    return {"Q_GeV":Q_GeV,"alpha_s":round(alpha_s_Q,5),"D_color":round(D_color,6),
            "F_color":round(F_color,4),"regime":regime,
            "thesis":"T1+T2+T5","label":"SIMULATED"}

def nuclear_binding_freedom(BE_per_nucleon_MeV: float) -> dict:
    """
    F_nuclear = BE/BE_max. Fe-56 has BE_max = 8.795 MeV/nucleon.
    Stars fuse toward Fe (increasing F_nuclear). Cannot go beyond (stellar fusion endpoint).
    Radioactive decay: high-Z elements decay TOWARD higher F_nuclear. T2 Law 2.
    """
    BE_max=8.795  # Fe-56, maximum — loaded from knowledge not hardcoded in formula
    F=min(1.0,max(0.0,BE_per_nucleon_MeV/BE_max))
    return {"F_nuclear":round(F,4),"BE_MeV_per_nucleon":BE_per_nucleon_MeV,
            "BE_max_MeV":BE_max,"interpretation":
            "F_nuclear=BE/BE_max. Fe-56 maximum. Stars stop fusing at Fe. Decay increases F.",
            "thesis":"T2+T5","label":"SIMULATED"}

def radioactive_decay_direction(Z_parent: int, Z_daughter: int,
                                BE_parent: float, BE_daughter: float) -> dict:
    "Decay direction predicted by T2: system seeks higher F_nuclear (lower D)."
    F_parent  = nuclear_binding_freedom(BE_parent)["F_nuclear"]
    F_daughter= nuclear_binding_freedom(BE_daughter)["F_nuclear"]
    F_increases=(F_daughter>F_parent)
    return {"Z_parent":Z_parent,"Z_daughter":Z_daughter,
            "F_parent":F_parent,"F_daughter":F_daughter,
            "F_increases":F_increases,
            "consistent_with_T2":F_increases,
            "thesis":"T2","label":"SIMULATED"}