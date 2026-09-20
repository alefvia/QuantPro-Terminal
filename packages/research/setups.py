from dataclasses import dataclass


@dataclass(frozen=True)
class SetupDefinition:
    name: str
    required_features: tuple[str, ...]
    description: str


CATALOG = (
    SetupDefinition(
        "trend_continuation",
        ("trend_aligned", "vwap_hold", "flow_aligned"),
        "Continuation after structure, VWAP and order flow align.",
    ),
    SetupDefinition(
        "vwap_reclaim",
        ("vwap_reclaim", "delta_turn", "structure_support"),
        "VWAP reclaim with improving executed-flow evidence.",
    ),
    SetupDefinition(
        "absorption_reversal",
        ("absorption", "failed_extension", "delta_divergence"),
        "Candidate reversal after absorption and failed price extension.",
    ),
    SetupDefinition(
        "liquidity_breakout",
        ("liquidity_consumed", "stacked_imbalance", "range_break"),
        "Breakout hypothesis after visible liquidity is consumed.",
    ),
    SetupDefinition(
        "exhaustion_reversal",
        ("exhaustion", "structure_reversal", "flow_turn"),
        "Reversal hypothesis after exhaustion plus structural confirmation.",
    ),
)


def matched_setups(features: dict[str, bool]) -> list[str]:
    return [
        setup.name
        for setup in CATALOG
        if all(features.get(feature, False) for feature in setup.required_features)
    ]
