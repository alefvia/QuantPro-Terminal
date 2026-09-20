from packages.core.maturity import PromotionEvidence
from packages.core.promotion import evaluate_promotion
from packages.monitoring.performance_guard import evaluate_recent
from packages.research.baseline import compare
from packages.research.labels import label_path


def test_forward_labels_include_mae_mfe_and_barriers():
    result = label_path([100, 101, 99, 103], 0, 3, target=0.02, stop=0.01)
    assert result.mfe == 0.03
    assert result.mae == -0.01
    assert result.hit_target
    assert result.hit_stop


def test_candidate_must_beat_baseline():
    result = compare([1.0, 2.0, 1.5], [0.1, 0.2, 0.0])
    assert result.beats_baseline
    assert result.uplift > 0


def test_recent_performance_fails_closed():
    assert not evaluate_recent([1.0] * 10).allowed
    assert not evaluate_recent([-1.0] * 30).allowed
    assert evaluate_recent([1.0] * 30).allowed


def test_promotion_requires_every_live_gate():
    evidence = PromotionEvidence(
        oos_positive=True,
        walk_forward_stable=True,
        paper_validated=True,
        feed_licensed=False,
        risk_controls_verified=True,
        explicit_live_authorization=False,
    )
    result = evaluate_promotion(evidence, [1.0] * 30, kill_switch_ready=True)
    assert not result.live_allowed
    assert "FEED_LICENSE_NOT_CONFIRMED" in result.reasons
    assert "EXPLICIT_LIVE_AUTHORIZATION_REQUIRED" in result.reasons
