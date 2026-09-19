from dataclasses import dataclass

@dataclass(frozen=True)
class TemporalSplit:
    train: slice
    validation: slice
    test: slice

def temporal_split(n: int, train_fraction: float = 0.60, validation_fraction: float = 0.20) -> TemporalSplit:
    if n < 10:
        raise ValueError("at least 10 observations required")
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1 or train_fraction+validation_fraction >= 1:
        raise ValueError("invalid fractions")
    train_end=int(n*train_fraction)
    val_end=train_end+int(n*validation_fraction)
    return TemporalSplit(slice(0,train_end),slice(train_end,val_end),slice(val_end,n))
