from dataclasses import dataclass

@dataclass(frozen=True)
class FeedCapabilities:
    provider: str
    realtime: bool
    trades: bool
    top_of_book: bool
    depth: bool
    mbo: bool
    licensed_for_use: bool

def allowed_for_intraday(cap: FeedCapabilities) -> tuple[bool,str]:
    if not cap.licensed_for_use:
        return False,"LICENSE_NOT_CONFIRMED"
    if not cap.realtime:
        return False,"NOT_REALTIME"
    if not cap.trades:
        return False,"NO_TRADES"
    return True,"OK"
