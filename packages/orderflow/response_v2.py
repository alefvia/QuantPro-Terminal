from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ResponseEvidence:
    absorption_bid: bool
    absorption_ask: bool
    exhaustion_candidate: bool
    price_response_ticks: Decimal
    evidence_count: int


def assess_response_v2(
    *,
    bid_volume: Decimal,
    ask_volume: Decimal,
    start: Decimal,
    end: Decimal,
    tick_size: Decimal,
    volume_threshold: Decimal,
    imbalance_ratio: Decimal = Decimal(2),
) -> ResponseEvidence:
    """Research primitive: requires volume + imbalance + limited adverse response."""
    if tick_size <= 0 or volume_threshold <= 0 or imbalance_ratio <= 0:
        raise ValueError("thresholds must be positive")
    move_ticks = (end - start) / tick_size
    bid_ratio = bid_volume / max(ask_volume, Decimal(1))
    ask_ratio = ask_volume / max(bid_volume, Decimal(1))
    absorption_bid = (
        bid_volume >= volume_threshold
        and bid_ratio >= imbalance_ratio
        and move_ticks >= Decimal(-1)
    )
    absorption_ask = (
        ask_volume >= volume_threshold
        and ask_ratio >= imbalance_ratio
        and move_ticks <= Decimal(1)
    )
    total = bid_volume + ask_volume
    exhaustion = total >= volume_threshold and abs(move_ticks) <= Decimal(1)
    count = sum((absorption_bid, absorption_ask, exhaustion))
    return ResponseEvidence(absorption_bid, absorption_ask, exhaustion, move_ticks, count)
