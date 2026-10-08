# Rithmic MNQ worker deployment

The code is ready for the user's part once a persistent container/VM is selected.

## Required runtime inputs

Mount the extracted licensed R|Protocol kit directory read-only and set:

- `RITHMIC_API_USER` — secret
- `RITHMIC_API_PASSWORD` — secret
- `RITHMIC_WSS_URL` — secret/config supplied by Rithmic; must begin with `wss://`
- `RITHMIC_KIT_DIR` — path to the mounted directory that contains `proto/` and `samples/`

Start with:

`python -m services.rithmic_mnq_worker`

The worker compiles the licensed protobuf schemas into a temporary directory at
runtime, logs into **Rithmic Test / Ticker Plant**, resolves the current MNQ front
month (templates 113/114), subscribes to last trade + BBO + order book and parses
Order Book template 156. It sends protocol heartbeats when traffic is idle and
reconnects after transient disconnects.

No order-plant connection or order-routing code exists in this worker.

## Why this is not deployed to Vercel

This is a continuously connected outbound WebSocket worker, not a request/response
web function. It requires a persistent process/container. The existing Vercel app
remains the UI. The worker should run on a persistent container/VM and feed the
QuantPro storage/API layer.

## First authenticated acceptance test

Success requires all of the following in Rithmic Test:

1. Login response code 0.
2. MNQ front-month response code 0 with a trading symbol.
3. Market-data subscription response code 0.
4. LastTrade events.
5. OrderBook template 156 events with multiple bid/ask levels.
6. Stable heartbeat/reconnect behavior.

Depth-by-Order/MBO is a separate entitlement test and remains disabled until the
above MBP path passes.
