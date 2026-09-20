from packages.data_engine.feed_gate import FeedCapabilities,allowed_for_intraday

def test_delayed_or_unlicensed_feed_is_rejected():
    delayed=FeedCapabilities("x",False,True,True,False,False,True)
    assert allowed_for_intraday(delayed)[0] is False
    unlicensed=FeedCapabilities("x",True,True,True,True,False,False)
    assert allowed_for_intraday(unlicensed)[0] is False

def test_licensed_realtime_trades_are_minimum_intraday_gate():
    cap=FeedCapabilities("x",True,True,False,False,False,True)
    assert allowed_for_intraday(cap)==(True,"OK")
