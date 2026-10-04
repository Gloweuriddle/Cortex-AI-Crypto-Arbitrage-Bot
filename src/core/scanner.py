"""
Cortex AI — Arbitrage Scanner
Fetches order books from multiple exchanges and computes spreads.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List

from src.exchanges.binance import BinanceClient
from src.exchanges.bybit import BybitClient
from src.exchanges.okx import OKXClient
from src.exchanges.htx import HTXClient
from src.utils.logger import get_logger

log = get_logger("cortex.scanner")


@dataclass
class ArbitrageOpportunity:
    """A single cross-exchange spread opportunity."""
    pair: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_pct: float
    profit_usd: float
    timestamp: float


class ArbitrageScanner:
    """Scans multiple exchanges and detects profitable spreads."""

    EXCHANGE_MAP = {
        "binance": BinanceClient,
        "bybit": BybitClient,
        "okx": OKXClient,
        "htx": HTXClient,
    }

    def __init__(self, exchanges: List[str], pairs: List[str]):
        self.pairs = pairs
        self.clients: Dict[str, object] = {}

        for name in exchanges:
            cls = self.EXCHANGE_MAP.get(name)
            if not cls:
                log.warning(f"Unknown exchange: {name}")
                continue
            self.clients[name] = cls()

    async def fetch_all(self) -> Dict[str, Dict[str, dict]]:
        """Fetch order books from all clients in parallel."""
        tasks = []
        for name, client in self.clients.items():
            for pair in self.pairs:
                tasks.append(self._fetch_one(name, client, pair))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate: {pair: {exchange: book}}
        books: Dict[str, Dict[str, dict]] = {p: {} for p in self.pairs}
        for r in results:
            if isinstance(r, Exception) or r is None:
                continue
            pair, exchange, book = r
            books[pair][exchange] = book
        return books

    async def _fetch_one(self, name, client, pair):
        try:
            book = await client.get_order_book(pair)
            return pair, name, book
        except Exception as exc:
            log.debug(f"{name} {pair}: {exc}")
            return None

    def find_spreads(
        self,
        books: Dict[str, Dict[str, dict]],
        min_spread_pct: float = 0.10,
    ) -> List[ArbitrageOpportunity]:
        """Compute best buy and sell across exchanges for each pair."""
        opportunities: List[ArbitrageOpportunity] = []

        for pair, exchanges in books.items():
            if len(exchanges) < 2:
                continue

            # Find lowest ask (buy) and highest bid (sell)
            cheapest = min(exchanges.items(), key=lambda kv: kv[1]["ask"])
            priciest = max(exchanges.items(), key=lambda kv: kv[1]["bid"])

            buy_exchange, buy_book = cheapest
            sell_exchange, sell_book = priciest

            buy_price = buy_book["ask"]
            sell_price = sell_book["bid"]

            if buy_price <= 0:
                continue

            spread_pct = (sell_price - buy_price) / buy_price * 100.0

            if spread_pct < min_spread_pct:
                continue

            profit_usd = sell_price - buy_price

            opportunities.append(
                ArbitrageOpportunity(
                    pair=pair,
                    buy_exchange=buy_exchange,
                    sell_exchange=sell_exchange,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    spread_pct=spread_pct,
                    profit_usd=profit_usd,
                    timestamp=asyncio.get_event_loop().time(),
                )
            )

        opportunities.sort(key=lambda o: o.spread_pct, reverse=True)
        return opportunities

    async def close(self) -> None:
        """Close all exchange clients."""
        for client in self.clients.values():
            close = getattr(client, "close", None)
            if close:
                await close()
