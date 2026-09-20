from dataclasses import dataclass


@dataclass(frozen=True)
class PurgedFold:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def purged_expanding_folds(
    n: int,
    train: int,
    test: int,
    purge: int = 0,
    embargo: int = 0,
) -> list[PurgedFold]:
    if min(n, train, test) <= 0 or purge < 0 or embargo < 0:
        raise ValueError("invalid fold sizes")
    folds: list[PurgedFold] = []
    train_end = train
    while True:
        test_start = train_end + purge
        test_end = test_start + test
        if test_end > n:
            break
        effective_train_end = max(0, train_end - embargo)
        if effective_train_end:
            folds.append(PurgedFold(0, effective_train_end, test_start, test_end))
        train_end = test_end
    return folds
