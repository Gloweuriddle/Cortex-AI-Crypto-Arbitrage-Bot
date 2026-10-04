"""
Cortex AI — Base Exchange Client
Abstract interface for all exchange integrations.
"""

from abc import ABC, abstractmethod
from typing import Optional

import aiohttp


class BaseExchange(ABC):
    """Abstract exchange client."""

    name: str = "base"
    base_url: str = ""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    @abstractmethod
    async def get_order_book(self, pair: str) -> dict:
        """Return {"bid": float, "ask": float} for the given pair."""
        ...

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
