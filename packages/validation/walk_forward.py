from dataclasses import dataclass

@dataclass(frozen=True)
class Fold:
    train_start: int
    train_end: int
    test_start: int
    test_end: int

def expanding_folds(n: int, train: int, test: int) -> list[Fold]:
    if min(n,train,test)<=0:
        raise ValueError("positive sizes required")
    out=[]
    end=train
    while end+test<=n:
        out.append(Fold(0,end,end,end+test))
        end+=test
    return out
