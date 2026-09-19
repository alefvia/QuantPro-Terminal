# F4 — Market Structure / Volume / Volatility

Implemented primitives:
- session VWAP
- ATR / true range
- realized volatility
- session range position
- baseline trend state
- volume profile with POC/VAH/VAL
- session high/low/midpoint

Planned feed-derived levels already represented in the terminal:
previous high/low, overnight high/low and opening range.

These engines calculate from supplied observations. They do not download or invent exchange prices. Until a legal NQ/GC futures feed is connected, the terminal must show OFFLINE/WAIT and Risk veto.
