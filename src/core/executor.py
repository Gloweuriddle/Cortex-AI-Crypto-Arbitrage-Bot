"""
Cortex AI — Order Executor
Executes approved arbitrage opportunities with risk checks.
"""

from src.core.scanner import ArbitrageOpportunity
from src.risk.manager import RiskManager
from src.utils.logger import get_logger

log = get_logger("cortex.executor")


class OrderExecutor:
    """Places orders on buy and sell exchanges for each opportunity."""

    def __init__(self, risk_manager: RiskManager, dry_run: bool = True):
        self.risk = risk_manager
        self.dry_run = dry_run
        if dry_run:
            log.warning("DRY-RUN mode enabled — no real orders will be placed")

    async def execute(self, op: ArbitrageOpportunity) -> bool:
        """Execute a single arbitrage opportunity."""
        size_usd = self.risk.position_size(op)

        if size_usd <= 0:
            log.debug(f"Skipped {op.pair} — size 0")
            return False

        log.info(
            f"[{op.pair}] BUY {op.buy_exchange} @ {op.buy_price:.4f} | "
            f"SELL {op.sell_exchange} @ {op.sell_price:.4f} | "
            f"spread={op.spread_pct:.3f}% | size=${size_usd:.2f}"
        )

        if self.dry_run:
            log.info("DRY-RUN: order not actually placed")
            return True

        # ---- REAL EXECUTION SECTION ----
        # In production:
        #   buy_order = await buy_client.market_buy(op.pair, size_usd)
        #   sell_order = await sell_client.market_sell(op.pair, size_usd)
        #   then verify fill, log P&L, update risk manager.
        #
        # This placeholder intentionally does NOT place real orders.
        # ---------------------------------

        return True
