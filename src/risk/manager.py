"""
Cortex AI — Risk Manager
Applies position sizing and exposure limits to every opportunity.
"""

from dataclasses import dataclass, field
from typing import List

from src.core.scanner import ArbitrageOpportunity
from src.utils.logger import get_logger

log = get_logger("cortex.risk")


@dataclass
class RiskManager:
    max_position_usd: float = 500.0
    max_daily_loss_usd: float = 100.0
    min_spread_pct: float = 0.10
    max_open_positions: int = 3

    open_positions: List[str] = field(default_factory=list)
    daily_pnl: float = 0.0

    def approve(self, op: ArbitrageOpportunity) -> bool:
        """Return True if the opportunity passes all risk checks."""
        if op.spread_pct < self.min_spread_pct:
            return False
        if len(self.open_positions) >= self.max_open_positions:
            log.debug("Max open positions reached")
            return False
        if self.daily_pnl <= -abs(self.max_daily_loss_usd):
            log.warning("Daily loss limit hit — stopping")
            return False
        return True

    def position_size(self, op: ArbitrageOpportunity) -> float:
        """Position size in USD based on spread and limits."""
        base = min(self.max_position_usd, 100.0)
        scaled = base * (op.spread_pct / 0.5)
        return round(min(scaled, self.max_position_usd), 2)
