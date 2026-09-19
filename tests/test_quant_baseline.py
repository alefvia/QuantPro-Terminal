import pytest
from packages.core.contracts import Decision
from packages.decision_engine.ensemble import ensemble
from packages.quant_engine.baseline import baseline_score
from packages.quant_engine.features import FeatureVector
from packages.quant_engine.split import temporal_split

def test_baseline_has_no_fake_probability():
    f=FeatureVector(.8,.7,.2,.6,.7,.1,0,.6)
    out=baseline_score(f)
    assert out.score>0
    assert out.calibrated_probability is None

def test_ensemble_disagreement_forces_wait():
    out=ensemble([.9,-.8,.8])
    assert out.decision==Decision.WAIT

def test_temporal_split_is_ordered():
    s=temporal_split(100)
    assert s.train==slice(0,60)
    assert s.validation==slice(60,80)
    assert s.test==slice(80,100)

def test_feature_guard():
    with pytest.raises(ValueError):
        baseline_score(FeatureVector(2,0,0,0,0,0,0,0))
