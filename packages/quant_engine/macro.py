from dataclasses import dataclass

@dataclass(frozen=True)
class MacroSnapshot:
    us_2y: float | None = None
    us_10y: float | None = None
    real_10y: float | None = None
    vix: float | None = None
    dollar_broad: float | None = None

def nq_context(current: MacroSnapshot, previous: MacroSnapshot) -> dict[str, int]:
    return {
        "rates_2y": _direction(previous.us_2y, current.us_2y, bullish_when_down=True),
        "real_yield": _direction(previous.real_10y, current.real_10y, bullish_when_down=True),
        "vix": _direction(previous.vix, current.vix, bullish_when_down=True),
        "dollar": _direction(previous.dollar_broad, current.dollar_broad, bullish_when_down=True),
    }

def gold_context(current: MacroSnapshot, previous: MacroSnapshot) -> dict[str, int]:
    return {
        "real_yield": _direction(previous.real_10y, current.real_10y, bullish_when_down=True),
        "dollar": _direction(previous.dollar_broad, current.dollar_broad, bullish_when_down=True),
        "vix": _direction(previous.vix, current.vix, bullish_when_down=False),
    }

def _direction(old: float | None, new: float | None, *, bullish_when_down: bool) -> int:
    if old is None or new is None or old == new:
        return 0
    down = new < old
    bullish = down if bullish_when_down else not down
    return 1 if bullish else -1
