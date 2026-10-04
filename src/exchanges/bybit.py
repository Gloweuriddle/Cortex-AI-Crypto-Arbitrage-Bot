"""
Cortex AI — ByBit Exchange Client
Public order book endpoint: /v5/market/orderbook
"""

from src.exchanges.base import BaseExchange


class BybitClient(BaseExchange):
    name = "bybit"
    base_url = "https://api.bybit.com"

    async def get_order_book(self, pair: str) -> dict:
        symbol = pair.replace("/", "")
        url = f"{self.base_url}/v5/market/orderbook"
        params = {"category": "spot", "symbol": symbol, "limit": 5}

        session = await self._get_session()
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

        result = data["result"]
        best_bid = float(result["b"][0][0])
        best_ask = float(result["a"][0][0])
        return {"bid": best_bid, "ask": best_ask}
