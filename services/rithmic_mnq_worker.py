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
"""Cloud Rithmic MNQ connector with authenticated read-only relay."""

import asyncio
import json
import logging
import os
from urllib.parse import quote

import httpx

from packages.data_engine.rithmic_mnq_client import RithmicMNQClient
from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig

RELAY_URL = os.getenv("QUANTPRO_RELAY_URL", "https://quantpro-readonly-relay.onrender.com/ingest")
RELAY_AUDIENCE = os.getenv("QUANTPRO_RELAY_AUDIENCE", "https://quantpro-readonly-relay.onrender.com")
METADATA_IDENTITY = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity"

def _terminal_symbol(symbol: str) -> str:
    for root in ("MNQ", "NQ", "MGC", "GC"):
        if symbol.upper().startswith(root):
            return root
    return symbol.upper()

def _payload(event) -> dict:
    return {
        "symbol": _terminal_symbol(event.symbol),
        "kind": event.kind,
        "observed_at": event.observed_at.isoformat(),
        "price": float(event.price),
        "size": float(event.size),
        "side": event.side,
    }

async def _relay_headers(client: httpx.AsyncClient) -> dict[str, str]:
    response = await client.get(
        f"{METADATA_IDENTITY}?audience={quote(RELAY_AUDIENCE, safe='')}&format=full",
        headers={"Metadata-Flavor": "Google"},
    )
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.text}"}

async def _forward_event(client: httpx.AsyncClient, event) -> None:
    token = os.getenv("QUANTPRO_INGEST_TOKEN")
    if not token:
        raise RuntimeError("QUANTPRO_INGEST_TOKEN is not configured")
    payload = _payload(event)
    local = await client.post(
        os.getenv("QUANTPRO_FEED_URL", "http://127.0.0.1:8000/feed/ingest"),
        headers={"X-Quantpro-Token": token},
        json=payload,
    )
    local.raise_for_status()
    try:
        relay = await client.post(RELAY_URL, headers=await _relay_headers(client), json=payload)
        relay.raise_for_status()
    except httpx.HTTPError:
        logging.exception("QuantPro relay ingest failed; local feed remains available")

async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    rithmic = RithmicMNQClient(RithmicRuntimeConfig.from_env())
    async with httpx.AsyncClient(timeout=8.0) as api:
        async for event in rithmic.stream():
            try:
                await _forward_event(api, event)
            except httpx.HTTPError:
                logging.exception("QuantPro local feed ingest failed; event will not be shown")
                continue
            print(json.dumps({
                "provider": event.provider, "symbol": _terminal_symbol(event.symbol),
                "kind": event.kind, "observed_at": event.observed_at.isoformat(),
                "price": str(event.price), "size": str(event.size), "side": event.side,
                "level": event.level,
            }, separators=(",", ":")), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
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
