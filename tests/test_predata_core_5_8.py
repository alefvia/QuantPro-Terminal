from packages.data_engine.adapters import ibkr_placeholder, rithmic_placeholder
from packages.macro_engine.reaction import ReactionWindow, assess_reaction
from packages.validation.advanced import CostModel, evaluate
from packages.validation.evidence import TradeResult
from packages.validation.purged import purged_expanding_folds


def test_costs_reduce_expectancy():
    rows = [TradeResult(2.0, -1.0, 3.0) for _ in range(100)]
    result = evaluate(rows, CostModel(commission=0.25, slippage=0.25))
    assert result.net_expectancy == 1.5
    assert result.passed


def test_purged_folds_separate_train_and_test():
    folds = purged_expanding_folds(100, 40, 10, purge=2, embargo=2)
    assert folds
    assert folds[0].train_end == 38
    assert folds[0].test_start == 42


def test_macro_reaction_fails_closed_without_data():
    result = assess_reaction(ReactionWindow("CPI", None))
    assert not result.usable


def test_macro_reaction_is_descriptive():
    result = assess_reaction(
        ReactionWindow(
            "CPI",
            surprise=0.2,
            nq_return=-0.01,
            gold_return=-0.005,
            yield_2y_change=0.08,
            dollar_return=0.006,
            cvd_change=-500,
        )
    )
    assert result.usable
    assert result.flow_alignment == 1.0


def test_vendor_adapters_fail_closed_until_authorized():
    for adapter in (rithmic_placeholder(), ibkr_placeholder()):
        assert not adapter.capabilities.realtime
        assert not adapter.capabilities.licensed
        try:
            adapter.connect()
        except RuntimeError:
            pass
        else:
            raise AssertionError("unconfigured adapter must not connect")
