"""Executable R|Protocol ticker-plant client for MNQ research ingestion.

The protobuf modules are supplied at runtime from the user's licensed Rithmic package.
This file deliberately contains no vendor source and no credentials.
"""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
import importlib
import sys

import websockets

from packages.data_engine.rithmic_protocol import normalize_depth, normalize_trade
from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig


class RithmicMNQClient:
    def __init__(self, config: RithmicRuntimeConfig) -> None:
        self.config = config
        proto_dir = str(config.proto_python_dir.resolve())
        if proto_dir not in sys.path:
            sys.path.insert(0, proto_dir)
        self.base = importlib.import_module("base_pb2")
        self.login_pb = importlib.import_module("request_login_pb2")
        self.login_response_pb = importlib.import_module("response_login_pb2")
        self.market_pb = importlib.import_module("request_market_data_update_pb2")
        self.market_response_pb = importlib.import_module("response_market_data_update_pb2")
        self.last_trade_pb = importlib.import_module("last_trade_pb2")
        self.bbo_pb = importlib.import_module("best_bid_offer_pb2")
        self.order_book_pb = importlib.import_module("order_book_pb2")

    async def _login(self, ws) -> None:
        rq = self.login_pb.RequestLogin()
        rq.template_id = 10
        rq.template_version = "5.55"
        rq.user = self.config.user
        rq.password = self.config.password
        rq.app_name = "QuantPro"
        rq.app_version = "0.1.0"
        rq.system_name = self.config.system_name
        rq.infra_type = self.login_pb.RequestLogin.SysInfraType.TICKER_PLANT
        await ws.send(rq.SerializeToString())
        raw = await asyncio.wait_for(ws.recv(), timeout=15)
        rp = self.login_response_pb.ResponseLogin()
        rp.ParseFromString(raw)
        if not rp.rp_code or rp.rp_code[0] != "0":
            raise RuntimeError(f"Rithmic login rejected: {list(rp.rp_code)}")

    async def _subscribe(self, ws, symbol: str) -> None:
        rq = self.market_pb.RequestMarketDataUpdate()
        rq.template_id = 100
        rq.symbol = symbol
        rq.exchange = self.config.exchange
        rq.request = self.market_pb.RequestMarketDataUpdate.Request.SUBSCRIBE
        rq.update_bits = (
            self.market_pb.RequestMarketDataUpdate.UpdateBits.LAST_TRADE
            | self.market_pb.RequestMarketDataUpdate.UpdateBits.BBO
            | self.market_pb.RequestMarketDataUpdate.UpdateBits.ORDER_BOOK
        )
        await ws.send(rq.SerializeToString())

    async def stream(self, trading_symbol: str):
        async with websockets.connect(
            self.config.websocket_url,
            ping_interval=3,
            open_timeout=15,
        ) as ws:
            await self._login(ws)
            await self._subscribe(ws, trading_symbol)
            async for raw in ws:
                base = self.base.Base()
                base.ParseFromString(raw)
                if base.template_id == 150:
                    msg = self.last_trade_pb.LastTrade()
                    msg.ParseFromString(raw)
                    aggressor = (
                        "buy"
                        if msg.aggressor == self.last_trade_pb.LastTrade.TransactionType.BUY
                        else "sell"
                    )
                    yield normalize_trade(
                        symbol=msg.symbol,
                        observed_at=datetime.fromtimestamp(
                            msg.ssboe + msg.usecs / 1_000_000, tz=UTC
                        ),
                        price=Decimal(str(msg.trade_price)),
                        size=Decimal(msg.trade_size_64),
                        aggressor=aggressor,
                    )
                elif base.template_id == 151:
                    # BBO is intentionally consumed by the protocol connection; the
                    # existing MarketEvent contract models one side at a time and depth
                    # messages provide the book events needed by Order Flow.
                    continue
                elif base.template_id == 152:
                    msg = self.order_book_pb.OrderBook()
                    msg.ParseFromString(raw)
                    side = "bid" if msg.book_type == 1 else "ask"
                    yield normalize_depth(
                        symbol=msg.symbol,
                        observed_at=datetime.fromtimestamp(
                            msg.ssboe + msg.usecs / 1_000_000, tz=UTC
                        ),
                        price=Decimal(str(msg.price)),
                        size=Decimal(msg.size),
                        side=side,
                    )
