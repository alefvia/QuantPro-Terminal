import argparse
from datetime import datetime
from pathlib import Path
from packages.data_engine.databento_historical import DEFAULT_SYMBOLS,HistoricalRequest,load_history

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    p.add_argument("--schema",default="ohlcv-1m")
    p.add_argument("--output",default="data/raw/databento/history.dbn")
    p.add_argument("--symbols",nargs="+",default=list(DEFAULT_SYMBOLS))
    return p.parse_args()

def main():
    a=parse_args()
    request=HistoricalRequest(tuple(a.symbols),datetime.fromisoformat(a.start),datetime.fromisoformat(a.end),a.schema)
    data=load_history(request)
    path=Path(a.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    data.to_file(path)
    print(path)

if __name__=="__main__":
    main()
