from dataclasses import dataclass
from enum import Enum

class Maturity(str,Enum):
    RESEARCH="RESEARCH"
    BACKTEST_VALIDATED="BACKTEST_VALIDATED"
    PAPER_VALIDATED="PAPER_VALIDATED"
    LIVE_ELIGIBLE="LIVE_ELIGIBLE"

@dataclass(frozen=True)
class PromotionEvidence:
    oos_positive: bool
    walk_forward_stable: bool
    paper_validated: bool
    feed_licensed: bool
    risk_controls_verified: bool
    explicit_live_authorization: bool

def highest_maturity(e: PromotionEvidence) -> Maturity:
    if not (e.oos_positive and e.walk_forward_stable):
        return Maturity.RESEARCH
    if not e.paper_validated:
        return Maturity.BACKTEST_VALIDATED
    if not (e.feed_licensed and e.risk_controls_verified and e.explicit_live_authorization):
        return Maturity.PAPER_VALIDATED
    return Maturity.LIVE_ELIGIBLE
