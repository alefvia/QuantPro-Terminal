from dataclasses import dataclass
from packages.quant_engine.features import FeatureVector

@dataclass(frozen=True)
class ModelOutput:
    score: float
    calibrated_probability: float | None
    model: str

DEFAULT_WEIGHTS=(0.22,0.14,0.10,0.16,0.16,0.08,0.08,0.06)

def baseline_score(features: FeatureVector, weights: tuple[float, ...] = DEFAULT_WEIGHTS) -> ModelOutput:
    values=features.values()
    if len(weights) != len(values):
        raise ValueError("weight count must match features")
    if any(abs(v)>1 for v in values):
        raise ValueError("features must be normalized to [-1,1]")
    score=sum(v*w for v,w in zip(values,weights,strict=True))/sum(abs(w) for w in weights)
    return ModelOutput(score=max(-1.0,min(1.0,score)), calibrated_probability=None, model="weighted-baseline-v1")
