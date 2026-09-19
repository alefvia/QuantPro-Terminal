from dataclasses import dataclass

@dataclass(frozen=True)
class Fold:
    train: slice
    test: slice

def expanding_walk_forward(n: int, train_size: int, test_size: int) -> list[Fold]:
    if train_size<=0 or test_size<=0 or train_size+test_size>n:
        raise ValueError("invalid walk-forward sizes")
    folds=[]
    end=train_size
    while end+test_size<=n:
        folds.append(Fold(slice(0,end),slice(end,end+test_size)))
        end+=test_size
    return folds
