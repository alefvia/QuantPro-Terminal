"""Minimal supervisor entrypoint for the cloud Rithmic MNQ connector."""

import asyncio
import json
import logging
import os

import httpx

from packages.data_engine.rithmic_mnq_client import RithmicMNQClient
from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig


def _terminal_symbol(symbol: str) -> str:
    """Map an exchange contract (for example MNQZ6) to the terminal market."""
    for root in ("MNQ", "NQ", "MGC", "GC"):
        if symbol.upper().startswith(root):
            return root
    return symbol.upper()


async def _forward_event(client: httpx.AsyncClient, event) -> None:
    endpoint = os.getenv("QUANTPRO_FEED_URL", "http://127.0.0.1:8000/feed/ingest")
    token = os.getenv("QUANTPRO_INGEST_TOKEN")
    if not token:
        raise RuntimeError("QUANTPRO_INGEST_TOKEN is not configured")
    response = await client.post(
        endpoint,
        headers={"X-Quantpro-Token": token},
        json={
            "symbol": _terminal_symbol(event.symbol),
            "kind": event.kind,
            "observed_at": event.observed_at.isoformat(),
            "price": float(event.price),
            "size": float(event.size),
            "side": event.side,
        },
    )
    response.raise_for_status()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = RithmicRuntimeConfig.from_env()
    rithmic = RithmicMNQClient(config)
    async with httpx.AsyncClient(timeout=5.0) as api:
        async for event in rithmic.stream():
            try:
                await _forward_event(api, event)
            except httpx.HTTPError:
                logging.exception("QuantPro feed ingest failed; event will not be shown")
                continue
            print(
                json.dumps(
                    {
                        "provider": event.provider,
                        "symbol": _terminal_symbol(event.symbol),
                        "kind": event.kind,
                        "observed_at": event.observed_at.isoformat(),
                        "price": str(event.price),
                        "size": str(event.size),
                        "side": event.side,
                        "level": event.level,
                    },
                    separators=(",", ":"),
                ),
                flush=True,
            )


if __name__ == "__main__":
    asyncio.run(main())
