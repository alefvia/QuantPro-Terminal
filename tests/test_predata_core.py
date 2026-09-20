from datetime import UTC, datetime
from decimal import Decimal

from packages.macro_engine.context import (
    EventTier,
    MacroEvent,
    dynamic_macro_weight,
    event_risk_multiplier,
)
from packages.orderflow.response_v2 import assess_response_v2
from packages.research.discovery import bonferroni_alpha, discover_binary_patterns, family_budget
from packages.research.setups import matched_setups


def test_high_impact_event_can_veto_new_risk():
    assert event_risk_multiplier(3, EventTier.HIGH) == 0.0
    assert dynamic_macro_weight(minutes_to_event=10, tier=EventTier.HIGH) == 0.30


def test_macro_surprise_is_actual_minus_consensus():
    event = MacroEvent("CPI", datetime.now(UTC), actual=3.2, consensus=3.0)
    assert round(event.surprise or 0, 2) == 0.20


def test_response_v2_requires_volume_imbalance_and_response():
    result = assess_response_v2(
        bid_volume=Decimal(100),
        ask_volume=Decimal(20),
        start=Decimal(100),
        end=Decimal("100.25"),
        tick_size=Decimal("0.25"),
        volume_threshold=Decimal(50),
    )
    assert result.absorption_bid
    assert result.price_response_ticks == Decimal(1)


def test_setup_catalog_matches_only_complete_evidence():
    features = {
        "trend_aligned": True,
        "vwap_hold": True,
        "flow_aligned": True,
        "absorption": False,
    }
    assert matched_setups(features) == ["trend_continuation"]


def test_discovery_enforces_minimum_occurrences():
    rows = [{"a": True, "b": True, "future": 1.0} for _ in range(35)]
    found = discover_binary_patterns(
        rows,
        feature_names=["a", "b"],
        target="future",
        min_features=2,
        max_features=2,
        min_occurrences=30,
    )
    assert found[0].features == ("a", "b")
    assert found[0].occurrences == 35


def test_multiple_testing_budget_is_explicit():
    assert family_budget(4, 2) == 10
    assert bonferroni_alpha(0.05, 10) == 0.005
