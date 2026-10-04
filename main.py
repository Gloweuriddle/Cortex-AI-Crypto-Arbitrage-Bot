"""
Cortex AI — Cross-Exchange Crypto Arbitrage Bot
Version: 3.4.0
License: MIT
Official site: https://runcortex.xyz/

This is the entry point of the bot. It initializes the engine,
loads the config, and starts the main scanning loop.
"""

import asyncio
import signal
import sys
from pathlib import Path

import yaml

from src.core.engine import CortexEngine
from src.utils.logger import get_logger

log = get_logger("cortex.main")


def load_config(path: str = "config.yaml") -> dict:
    """Load YAML configuration from disk."""
    config_path = Path(path)
    if not config_path.exists():
        log.error(f"Config file not found: {path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def run() -> None:
    """Main async entry point."""
    log.info("=" * 60)
    log.info("  Cortex AI v3.4.0 — Cross-Exchange Arbitrage Engine")
    log.info("  Non-custodial · Open-source · Local-first")
    log.info("=" * 60)

    config = load_config()
    engine = CortexEngine(config)

    # Graceful shutdown on Ctrl+C
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, engine.stop)

    try:
        await engine.start()
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as exc:
        log.exception(f"Fatal error: {exc}")
        sys.exit(1)
