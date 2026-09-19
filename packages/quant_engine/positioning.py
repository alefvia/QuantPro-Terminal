from dataclasses import dataclass

@dataclass(frozen=True)
class Positioning:
    net: float
    change_1w: float
    percentile: float | None

def net_position(long: float, short: float) -> float:
    return long - short

def percentile_rank(history: list[float], current: float) -> float | None:
    if not history:
        return None
    return sum(x <= current for x in history) / len(history)

def positioning(long: float, short: float, prior_net: float, history: list[float]) -> Positioning:
    net = net_position(long, short)
    return Positioning(net=net, change_1w=net-prior_net, percentile=percentile_rank(history, net))
