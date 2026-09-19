from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Relationship:
    correlation: float | None
    beta: float | None

def _returns(values: list[float]) -> list[float]:
    if len(values) < 2 or any(x <= 0 for x in values):
        return []
    return [math.log(values[i] / values[i - 1]) for i in range(1, len(values))]

def relationship(asset: list[float], driver: list[float]) -> Relationship:
    a, d = _returns(asset), _returns(driver)
    n = min(len(a), len(d))
    if n < 3:
        return Relationship(None, None)
    a, d = a[-n:], d[-n:]
    ma, md = sum(a)/n, sum(d)/n
    cov = sum((x-ma)*(y-md) for x,y in zip(a,d,strict=True))/(n-1)
    va = sum((x-ma)**2 for x in a)/(n-1)
    vd = sum((y-md)**2 for y in d)/(n-1)
    if va <= 0 or vd <= 0:
        return Relationship(None, None)
    return Relationship(correlation=cov/math.sqrt(va*vd), beta=cov/vd)

def rolling_relationship(asset: list[float], driver: list[float], window: int = 20) -> Relationship:
    if window < 4:
        raise ValueError("window must be >= 4")
    return relationship(asset[-(window+1):], driver[-(window+1):])
