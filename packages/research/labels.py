from dataclasses import dataclass


@dataclass(frozen=True)
class ForwardLabel:
    forward_return: float
    mae: float
    mfe: float
    hit_target: bool
    hit_stop: bool


def label_path(prices: list[float], entry_index: int, horizon: int, target: float, stop: float) -> ForwardLabel:
    if not prices or entry_index < 0 or horizon < 1 or entry_index >= len(prices) - 1:
        raise ValueError("invalid path")
    entry = prices[entry_index]
    if entry <= 0:
        raise ValueError("entry must be positive")
    future = prices[entry_index + 1 : min(len(prices), entry_index + horizon + 1)]
    changes = [(price - entry) / entry for price in future]
    return ForwardLabel(
        forward_return=changes[-1],
        mae=min(changes),
        mfe=max(changes),
        hit_target=any(change >= target for change in changes),
        hit_stop=any(change <= -abs(stop) for change in changes),
    )
