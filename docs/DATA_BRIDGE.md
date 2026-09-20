# QuantPro Data Bridge

The bridge is the controlled boundary between an authorized market-data adapter and QuantPro.

POST /feed/ingest requires QUANTPRO_INGEST_TOKEN through the X-Quantpro-Token header. The secret must exist only in environment configuration and must never be committed.

Packets preserve their original timezone-aware market timestamp. The store rejects unsupported symbols, invalid values and out-of-order events.

GET /feed/status exposes only safe operational state.

This bridge does not grant exchange redistribution rights. Any Sierra/Denali/Rithmic/other adapter must comply with its provider and exchange licensing. No live execution is enabled.
