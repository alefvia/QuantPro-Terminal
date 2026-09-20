from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class AbsorptionAssessment:
    bid_confirmed: bool
    ask_confirmed: bool
    exhaustion: bool

def assess_response(*,bid_volume: Decimal,ask_volume: Decimal,start: Decimal,end: Decimal,threshold: Decimal) -> AbsorptionAssessment:
    move=end-start
    bid_confirmed=bid_volume>=threshold and move>=0
    ask_confirmed=ask_volume>=threshold and move<=0
    exhaustion=abs(move)==0 and (bid_volume>=threshold or ask_volume>=threshold)
    return AbsorptionAssessment(bid_confirmed,ask_confirmed,exhaustion)
