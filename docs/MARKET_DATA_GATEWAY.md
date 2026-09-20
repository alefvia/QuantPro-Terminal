# Market Data Gateway

Provider-neutral ingestion boundary for QuantPro.

Provider feed -> adapter -> normalized events -> Order Flow -> Quant/Decision/Risk.

Research/replay may use delayed data. Realtime use requires a licensed realtime feed. Providers remain replaceable; MBO remains optional.
