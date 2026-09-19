# Canonical Data Schema — F2

## Time
All timestamps are timezone-aware. UTC is canonical at storage boundaries.

## Long-form observation
| field | meaning |
|---|---|
| observed_at | time/date represented by the observation |
| available_at | earliest proven time the platform had access to it |
| source | provider |
| series | canonical/provider series key |
| value | numeric observation |

## Storage
- Raw: immutable source snapshots when licensing permits.
- Processed: Parquet, partitioned by provider/series as volume grows.
- Manifests: SHA-256, row count, source, generation time.
- PostgreSQL/Timescale is an online-serving layer, not the sole research archive.

## Anti-look-ahead
Research queries use available_at <= decision timestamp. Revised macro data must not be silently substituted into historical decisions; ALFRED/vintages will be introduced where release-level historical fidelity is required.
