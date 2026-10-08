"""Minimal supervisor entrypoint for the cloud Rithmic MNQ connector."""

import asyncio
import json

from packages.data_engine.rithmic_mnq_client import RithmicMNQClient
from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig


async def main() -> None:
    config = RithmicRuntimeConfig.from_env()
    client = RithmicMNQClient(config)
    async for event in client.stream():
        # Temporary durable-boundary format. The next storage adapter can consume
        # this JSON stream without changing the Rithmic protocol client.
        print(
            json.dumps(
                {
                    "provider": event.provider,
                    "symbol": event.symbol,
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
