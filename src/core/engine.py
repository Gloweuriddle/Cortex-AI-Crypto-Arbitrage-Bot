"""
Cortex AI — Core Engine
Orchestrates the scanner, strategy, and executor loops.
"""

import asyncio
from typing import Dict, List

from src.core.scanner import ArbitrageScanner
from src.core.executor import OrderExecutor
from src.risk.manager import RiskManager
from src.utils.logger import get_logger

log = get_logger("cortex.engine")


class CortexEngine:
    """Main runtime orchestrator."""

    def __init__(self, config: dict):
        self.config = config
        self.running = False

        # Build scanner from exchange config
        self.scanner = ArbitrageScanner(
            exchanges=config["exchanges"],
            pairs=config["pairs"],
        )

        self.risk = RiskManager(config["risk"])
        self.executor = OrderExecutor(
            risk_manager=self.risk,
            dry_run=config.get("dry_run", True),
        )

    async def start(self) -> None:
        """Start the main event loop."""
        self.running = True
        log.info("Engine starting...")

        interval = self.config["scanner"]["interval_ms"] / 1000.0
        log.info(f"Scanning {len(self.config['pairs'])} pairs every {interval}s")

        while self.running:
            try:
                await self._tick()
            except Exception as exc:
                log.exception(f"Tick error: {exc}")
            await asyncio.sleep(interval)

    async def _tick(self) -> None:
        """Single scan + strategy + execution cycle."""
        # 1. Fetch order books from all exchanges in parallel
        order_books = await self.scanner.fetch_all()

        # 2. Find profitable spreads
        opportunities = self.scanner.find_spreads(
            order_books,
            min_spread_pct=self.config["scanner"]["min_spread_pct"],
        )

        if not opportunities:
            return

        log.info(f"Found {len(opportunities)} arbitrage opportunities")

        # 3. Filter by risk manager
        approved = [op for op in opportunities if self.risk.approve(op)]

        # 4. Execute approved opportunities
        for op in approved:
            await self.executor.execute(op)

    def stop(self) -> None:
        """Request graceful shutdown."""
        log.info("Shutdown requested")
        self.running = False

    async def shutdown(self) -> None:
        """Cleanup before exit."""
        log.info("Shutting down engine...")
        await self.scanner.close()
        log.info("Bye.")
