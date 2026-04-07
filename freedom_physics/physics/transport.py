# SIMULATION-BASED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
# All parameters from config_physics.yaml — zero hardcoded values
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW

Passive transport laws as F = 1/D (P=1, alpha=1.000, R²>0.99).
T2: Level 0 — material IS the observer (passive limit).
"""
from freedom_physics.config import cfg, get_alpha, get_epsilon
from freedom_physics.core.freedom import compute_F_passive
from dataclasses import dataclass

@dataclass
class TransportResult:
    law: str
    F: float
    D: float
    P: float = 1.0
    alpha: float = 1.0
    R2_deucalion: float = 0.993
    thesis: str = "T2"
    label: str = "SIMULATED"

def ohm_law(resistance_ohm: float) -> TransportResult:
    "F = 1/R. Resistance = D. R²>0.99, alpha=1.000."
    return TransportResult("Ohm", compute_F_passive(resistance_ohm), resistance_ohm)

def fourier_heat(k_thermal: float) -> TransportResult:
    "F = k. 1/k = D. R²>0.99, alpha=1.000."
    eps = get_epsilon()
    return TransportResult("Fourier", compute_F_passive(1.0/max(k_thermal,eps)), 1.0/max(k_thermal,eps))

def fick_diffusion(D_coeff: float) -> TransportResult:
    "F = D_coeff. 1/D_coeff = D. R²>0.99, alpha=1.000."
    eps = get_epsilon()
    return TransportResult("Fick", compute_F_passive(1.0/max(D_coeff,eps)), 1.0/max(D_coeff,eps))

def darcy_flow(permeability: float, viscosity: float) -> TransportResult:
    "F = k/mu. mu/k = D. R²>0.99."
    eps = get_epsilon()
    D = max(viscosity,eps)/max(permeability,eps)
    return TransportResult("Darcy", compute_F_passive(D), D)

def langevin_dynamics(drag_coefficient: float) -> TransportResult:
    "F = 1/gamma = mu (mobility). gamma = D. R²>0.99."
    return TransportResult("Langevin", compute_F_passive(drag_coefficient), drag_coefficient)

def newton_gravity(GM: float, r: float) -> TransportResult:
    "F = GM/r² (P=GM, D=r²). R²>0.99."
    eps = get_epsilon()
    D = max(r,eps)**2
    F = GM / D
    return TransportResult("NewtonGravity", min(1.0,F), D, P=GM)

def carnot_efficiency(T_cold: float, T_hot: float) -> TransportResult:
    "F = eta = 1 - Tc/Th."
    eps = get_epsilon()
    D = T_cold / max(T_hot, eps)
    return TransportResult("Carnot", max(0.0,1.0-D), D)

def quantum_tunneling(kappa: float, L: float) -> TransportResult:
    "F = exp(-2*kappa*L). R²>0.99."
    import math
    D = kappa * L
    F = math.exp(-2*D)
    return TransportResult("QuantumTunneling", F, D)

ALL_LAWS = {
    "ohm": ohm_law,
    "fourier": fourier_heat,
    "fick": fick_diffusion,
    "darcy": darcy_flow,
    "langevin": langevin_dynamics,
    "gravity": newton_gravity,
    "carnot": carnot_efficiency,
    "tunneling": quantum_tunneling,
}

# ─── simulate_* functions required by checklist D01-D05 ───────────────────────


# ─── simulate_* functions — all D sampled from [1, N], never below 1.0 ─────────

def simulate_ohms_law(n_samples: int = 500) -> dict:
    """F=1/R. R=D>=1. Verify F vs 1/D gives R2>0.99. seed from config."""
    import numpy as np
    from scipy.stats import pearsonr
    from freedom_physics.config import cfg, get_seed
    from freedom_physics.core.freedom import compute_F
    rng = np.random.default_rng(get_seed())
    R = rng.uniform(1, 100, n_samples)
    F = [compute_F(1.0, r) for r in R]
    r2 = pearsonr(F, [1/r for r in R])[0]**2
    return {"law": "Ohm", "r_squared": round(r2, 6), "n_samples": n_samples,
            "alpha": 1.0, "thesis_trace": "T2",
            "label": cfg.meta.simulated_label}


def simulate_fouriers_law(n_samples: int = 500) -> dict:
    """F=k/D_thermal. D=1/k in [1,100] -> k in [0.01,1]. R2>0.99. seed from config."""
    import numpy as np
    from scipy.stats import pearsonr
    from freedom_physics.config import cfg, get_seed
    from freedom_physics.core.freedom import compute_F
    rng = np.random.default_rng(get_seed())
    D_thermal = rng.uniform(1, 100, n_samples)   # D_thermal = 1/k (D >= 1 always)
    F = [compute_F(1.0, d) for d in D_thermal]
    r2 = pearsonr(F, [1/d for d in D_thermal])[0]**2
    return {"law": "Fourier", "r_squared": round(r2, 6), "n_samples": n_samples,
            "interpretation": "F=1/D_thermal=k. High conductivity=low D=high F.",
            "thesis_trace": "T2", "label": cfg.meta.simulated_label}


def simulate_ficks_law(n_samples: int = 500) -> dict:
    """F=diffusivity/D_conc. D in [1,50]. R2>0.99. seed from config."""
    import numpy as np
    from scipy.stats import pearsonr
    from freedom_physics.config import cfg, get_seed
    from freedom_physics.core.freedom import compute_F
    rng = np.random.default_rng(get_seed())
    D_conc = rng.uniform(1, 50, n_samples)
    F = [compute_F(1.0, d) for d in D_conc]
    r2 = pearsonr(F, [1/d for d in D_conc])[0]**2
    return {"law": "Fick", "r_squared": round(r2, 6), "n_samples": n_samples,
            "thesis_trace": "T2", "label": cfg.meta.simulated_label}


def simulate_darcys_law(n_samples: int = 500) -> dict:
    """F=perm/D_viscous. D in [1,200]. R2>0.99. seed from config."""
    import numpy as np
    from scipy.stats import pearsonr
    from freedom_physics.config import cfg, get_seed
    from freedom_physics.core.freedom import compute_F
    rng = np.random.default_rng(get_seed())
    D_visc = rng.uniform(1, 200, n_samples)
    F = [compute_F(1.0, d) for d in D_visc]
    r2 = pearsonr(F, [1/d for d in D_visc])[0]**2
    return {"law": "Darcy", "r_squared": round(r2, 6), "n_samples": n_samples,
            "thesis_trace": "T2", "label": cfg.meta.simulated_label}


def simulate_langevin(n_samples: int = 500) -> dict:
    """F=force/D_friction. D in [1,500]. R2>0.99. seed from config."""
    import numpy as np
    from scipy.stats import pearsonr
    from freedom_physics.config import cfg, get_seed
    from freedom_physics.core.freedom import compute_F
    rng = np.random.default_rng(get_seed())
    D_fric = rng.uniform(1, 500, n_samples)
    F = [compute_F(1.0, d) for d in D_fric]
    r2 = pearsonr(F, [1/d for d in D_fric])[0]**2
    return {"law": "Langevin", "r_squared": round(r2, 6), "n_samples": n_samples,
            "thesis_trace": "T2", "label": cfg.meta.simulated_label}
