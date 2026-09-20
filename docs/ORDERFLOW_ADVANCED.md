# Advanced Order Flow research layer

Adds provider-neutral primitives for:
- cumulative executed delta;
- per-price bid/ask executed volume (footprint foundation);
- configurable executed-volume imbalance;
- configurable absorption candidates;
- Brazil-local 19:00-22:00 research window for NQ/MNQ vs GC/MGC.

These are research features, not trade signals. Thresholds are configurable and must be calibrated out-of-sample. Absorption is initially a candidate flag based on executed volume; price-response confirmation is a subsequent refinement.

No profitability or probability claim is made. Live remains blocked.
