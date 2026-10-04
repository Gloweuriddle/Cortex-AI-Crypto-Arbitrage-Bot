"""
Cortex AI — Binance Exchange Client
Public order book endpoint: /api/v3/depth
"""

from src.exchanges.base import BaseExchange
from src.utils.logger import get_logger

log = get_logger("cortex.exchanges.binance")


class BinanceClient(BaseExchange):
    name = "binance"
    base_url = "https://api.binance.com"

    async def get_order_book(self, pair: str) -> dict:
        """Fetch top of book from Binance."""
        symbol = pair.replace("/", "")
        url = f"{self.base_url}/api/v3/depth"
        params = {"symbol": symbol, "limit": 5}

        session = await self._get_session()
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

        best_bid = float(data["bids"][0][0])
        best_ask = float(data["asks"][0][0])
        return {"bid": best_bid, "ask": best_ask}
