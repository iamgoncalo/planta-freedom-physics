
"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW"""
import math
_EPS=1e-14
def distortion_geometric(channels, weights):
    assert abs(sum(weights.values())-1.0)<1e-6
    ln_D = sum(weights[k]*math.log(max(channels[k],1.0)) for k in channels)
    D    = math.exp(ln_D)
    if ln_D<_EPS: return D,{k:0.0 for k in channels}
    attr = {k:weights[k]*math.log(max(channels[k],1.0))/ln_D*100.0 for k in channels}
    return D, attr
