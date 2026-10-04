"""
Cortex AI — HTX Exchange Client
Public order book endpoint: /market/depth
"""

from src.exchanges.base import BaseExchange


class HTXClient(BaseExchange):
    name = "htx"
    base_url = "https://api.huobi.pro"

    async def get_order_book(self, pair: str) -> dict:
        symbol = pair.replace("/", "").lower()
        url = f"{self.base_url}/market/depth"
        params = {"symbol": symbol, "type": "step0"}

        session = await self._get_session()
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

        tick = data["tick"]
        best_bid = float(tick["bids"][0][0])
        best_ask = float(tick["asks"][0][0])
        return {"bid": best_bid, "ask": best_ask}
