"""
Cortex AI — OKX Exchange Client
Public order book endpoint: /api/v5/market/books
"""

from src.exchanges.base import BaseExchange


class OKXClient(BaseExchange):
    name = "okx"
    base_url = "https://www.okx.com"

    async def get_order_book(self, pair: str) -> dict:
        inst_id = pair.replace("/", "-")
        url = f"{self.base_url}/api/v5/market/books"
        params = {"instId": inst_id, "sz": 5}

        session = await self._get_session()
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

        book = data["data"][0]
        best_bid = float(book["bids"][0][0])
        best_ask = float(book["asks"][0][0])
        return {"bid": best_bid, "ask": best_ask}
