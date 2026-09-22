# Rithmic MNQ integration

Status: **official R|Protocol 0.90.0.0 package received; runtime credential injection and authenticated test pending**.

## Confirmed from the supplied official package

The package contains the reference guide, Protocol Buffer definitions and working
Python/JavaScript samples. The market-data protocol explicitly supports last trade,
best bid/offer and order book subscriptions. It also includes Depth-by-Order snapshot
and update request/response definitions, so the protocol has an MBO path; actual user
entitlement still must be verified after authentication.

The approved development system is **Rithmic Test**. The server requires secure
WebSocket (WSS). Credentials are intentionally not stored in this repository.

## MNQ-only pipeline

`R|Protocol Ticker Plant -> MNQ trades/BBO/order book -> MarketEvent -> Order Flow -> Decision/Risk`

The active MNQ contract will be resolved using the protocol's front-month/reference
messages instead of hard-coding a contract month.

## Connection sequence

1. Open WSS and request Rithmic system information.
2. Close that discovery connection as directed by Rithmic.
3. Open a new WSS connection.
4. Login to **Rithmic Test** using the Ticker Plant infrastructure.
5. Resolve the current MNQ front-month contract/reference data.
6. Subscribe to LAST_TRADE + BBO + ORDER_BOOK.
7. Normalize and persist every accepted event before feature calculation.
8. Maintain heartbeat/reconnect handling and fail closed on gaps.
9. Test Depth-by-Order separately; enable MBO features only if entitlement is confirmed.

## Deployment secrets

Runtime only:
- API user
- API password
- approved WSS endpoint

Never commit credentials, screenshots with identifiers, or vendor-licensed protocol
sources unless their license explicitly permits repository redistribution.

## Current gate

The adapter and protocol mapping can now be implemented without guessing. The next
external action is to inject the user's API credentials into a secure runtime secret
store and perform the first authenticated **Rithmic Test** connection. Live order
routing remains disabled.
