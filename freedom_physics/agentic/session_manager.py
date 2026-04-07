"""SIMULATED — F=P/D HYPOTHESIS UNDER TEST — NOT A PROVEN LAW
agentic/session_manager.py — Multi-turn session state + cost tracking.
Cost limits from cfg.ai_agents (never hardcoded).
Caching: TTL from cfg.ai_agents.cache_ttl_seconds.
"""
from __future__ import annotations
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from freedom_physics.config import cfg, get_seed


class SessionManager:
    def __init__(self):
        self.cfg              = cfg
        self.cost_limit_day   = float(cfg.ai_agents.cost_limit_day_eur)
        self.cost_limit_month = float(cfg.ai_agents.cost_limit_month_eur)
        self.cache_ttl        = int(cfg.ai_agents.cache_ttl_seconds)
        self._cache:  dict = {}
        self._costs:  list = []
        self._history:list = []
        self._state:  dict = {}

    def get_cost_today(self) -> float:
        now = time.time()
        return sum(c["cost"] for c in self._costs if now - c["ts"] < 86400)

    def check_budget(self) -> bool:
        return self.get_cost_today() < self.cost_limit_day

    def record_cost(self, cost_eur: float, agent: str):
        self._costs.append({"cost": cost_eur, "agent": agent, "ts": time.time()})

    def get_cached_or_call(self, query: str, mock: bool = False) -> dict:
        if query in self._cache:
            entry = self._cache[query]
            if time.time() - entry["ts"] < self.cache_ttl:
                return entry["result"]
        if mock:
            result = {"answer": f"Mock response for: {query[:40]}",
                      "label": cfg.meta.simulated_label}
        else:
            result = {"answer": "Real LLM call would go here",
                      "label": cfg.meta.simulated_label}
        self._cache[query] = {"result": result, "ts": time.time()}
        return result

    def save_state(self, key: str, value):
        self._state[key] = value

    def get_state(self, key: str, default=None):
        return self._state.get(key, default)
