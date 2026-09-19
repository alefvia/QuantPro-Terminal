from dataclasses import dataclass

@dataclass(frozen=True)
class VolumeProfile:
    poc: float
    vah: float
    val: float
    total_volume: float

def build_volume_profile(prices: list[float], volumes: list[float], value_area: float = 0.70) -> VolumeProfile:
    if len(prices) != len(volumes) or not prices:
        raise ValueError("prices and volumes must have equal non-zero length")
    if not 0 < value_area <= 1:
        raise ValueError("value_area must be in (0, 1]")
    buckets: dict[float, float] = {}
    for price, volume in zip(prices, volumes, strict=True):
        buckets[price] = buckets.get(price, 0.0) + volume
    total=sum(buckets.values())
    if total <= 0:
        raise ValueError("total volume must be positive")
    poc=max(buckets, key=buckets.get)
    ranked=sorted(buckets.items(), key=lambda x:x[1], reverse=True)
    selected=[]
    accumulated=0.0
    for price, volume in ranked:
        selected.append(price)
        accumulated += volume
        if accumulated >= total*value_area:
            break
    return VolumeProfile(poc=poc, vah=max(selected), val=min(selected), total_volume=total)
