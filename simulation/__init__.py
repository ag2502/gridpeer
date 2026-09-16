"""simulation package: market clearing mechanism + household environment.

Consumes AgentDecision, produces TradeEvent and MarketState — see shared/schemas.py.
"""

from simulation.market import clear_tick, trade_id

__all__ = ["clear_tick", "trade_id"]
