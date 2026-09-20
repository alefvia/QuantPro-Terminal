from dataclasses import dataclass
import math

@dataclass(frozen=True)
class DriftResult:
    drifted: bool
    mean_shift_z: float | None
    reason: str

def mean_shift(reference: list[float],current: list[float],threshold_z: float=2.0) -> DriftResult:
    if len(reference)<2 or not current:
        return DriftResult(False,None,"INSUFFICIENT_DATA")
    mean=sum(reference)/len(reference)
    variance=sum((x-mean)**2 for x in reference)/(len(reference)-1)
    if variance<=0:
        return DriftResult(False,None,"ZERO_REFERENCE_VARIANCE")
    z=abs((sum(current)/len(current)-mean)/math.sqrt(variance))
    return DriftResult(z>=threshold_z,z,"DRIFT" if z>=threshold_z else "OK")
