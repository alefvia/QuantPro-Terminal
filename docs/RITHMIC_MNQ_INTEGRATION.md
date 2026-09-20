# Rithmic MNQ integration

Status: **adapter prepared; official Dev Kit/access pending**.

## Scope

QuantPro will connect only the CME Micro E-mini Nasdaq-100 path first. The contract
must be resolved from Rithmic reference data/front-month metadata instead of being
hard-coded, so rollover does not silently leave the system on an expired contract.

Pipeline:

`R|Protocol WebSocket/protobuf -> Rithmic adapter -> MarketEvent -> Order Flow -> Decision/Risk`

## Evidence already obtained

The R|Trader Pro paper environment has been manually observed receiving MNQ quotes
and multi-level DOM/market depth. This is evidence for the account/UI entitlement,
not proof that the API entitlement or MBO stream is enabled.

## Safety / secrets

- Never commit username, password, API credentials, endpoints supplied under the Dev Kit,
  or screenshots containing account identifiers.
- Environment/runtime secrets only.
- Live order routing remains disabled.
- MBO remains unclaimed until verified through the API.
- No unofficial endpoint is guessed.
- Adapter fails closed until app name, app version and WebSocket URL are supplied from
  the official Rithmic developer material.

## Dev Kit handoff

When Rithmic supplies the Protocol kit:

1. Add the official protobuf definitions/bindings according to its license.
2. Configure application name/version and approved WebSocket endpoint as secrets.
3. Authenticate in the approved test/paper environment.
4. Resolve the active MNQ contract through reference data.
5. Subscribe to last trades, bid/ask and order book/depth.
6. Preserve Rithmic sequence/update semantics and rebuild snapshots atomically.
7. Map trades/depth into `MarketEvent`.
8. Record raw normalized events before feature calculation for deterministic replay.
9. Verify reconnect/gap detection and fail closed on sequence loss.
10. Separately test MBO entitlement before enabling Level-3 features.

No production/live trading promotion is authorized by this integration.
