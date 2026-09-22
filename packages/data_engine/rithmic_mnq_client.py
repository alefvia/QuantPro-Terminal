"""R|Protocol ticker-plant client for MNQ market-data ingestion.

Uses only runtime-generated bindings from the user's licensed Rithmic kit. It performs
no order routing. The active MNQ contract is resolved with the official front-month
request before market-data subscription.
"""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
import importlib
import sys

import websockets

from packages.data_engine.rithmic_proto_runtime import compile_rithmic_protos
from packages.data_engine.rithmic_protocol import normalize_depth, normalize_trade
from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig


class RithmicMNQClient:
    def __init__(self, config: RithmicRuntimeConfig) -> None:
        self.config = config
        generated = str(compile_rithmic_protos(config.kit_dir))
        if generated not in sys.path:
            sys.path.insert(0, generated)
        self.base = importlib.import_module("base_pb2")
        self.login_pb = importlib.import_module("request_login_pb2")
        self.login_response_pb = importlib.import_module("response_login_pb2")
        self.heartbeat_pb = importlib.import_module("request_heartbeat_pb2")
        self.front_pb = importlib.import_module("request_front_month_contract_pb2")
        self.front_response_pb = importlib.import_module("response_front_month_contract_pb2")
        self.market_pb = importlib.import_module("request_market_data_update_pb2")
        self.market_response_pb = importlib.import_module("response_market_data_update_pb2")
        self.last_trade_pb = importlib.import_module("last_trade_pb2")
        self.bbo_pb = importlib.import_module("best_bid_offer_pb2")
        self.order_book_pb = importlib.import_module("order_book_pb2")

    async def _login(self, ws) -> int:
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
        return int(rp.heartbeat_interval or 10)

    async def _heartbeat(self, ws) -> None:
        rq = self.heartbeat_pb.RequestHeartbeat()
        rq.template_id = 18
        await ws.send(rq.SerializeToString())

    async def _front_month(self, ws) -> tuple[str, str]:
        rq = self.front_pb.RequestFrontMonthContract()
        rq.template_id = 113
        rq.symbol = self.config.root_symbol
        rq.exchange = self.config.exchange
        rq.need_updates = True
        await ws.send(rq.SerializeToString())
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=15)
            base = self.base.Base()
            base.ParseFromString(raw)
            if base.template_id != 114:
                continue
            rp = self.front_response_pb.ResponseFrontMonthContract()
            rp.ParseFromString(raw)
            if rp.rp_code and rp.rp_code[0] != "0":
                raise RuntimeError(f"Front-month lookup rejected: {list(rp.rp_code)}")
            if not rp.trading_symbol:
                raise RuntimeError("Rithmic returned no MNQ front-month trading symbol")
            return rp.trading_symbol, rp.trading_exchange or self.config.exchange

    async def _subscribe(self, ws, symbol: str, exchange: str) -> None:
        rq = self.market_pb.RequestMarketDataUpdate()
        rq.template_id = 100
        rq.symbol = symbol
        rq.exchange = exchange
        rq.request = self.market_pb.RequestMarketDataUpdate.Request.SUBSCRIBE
        rq.update_bits = (
            self.market_pb.RequestMarketDataUpdate.UpdateBits.LAST_TRADE
            | self.market_pb.RequestMarketDataUpdate.UpdateBits.BBO
            | self.market_pb.RequestMarketDataUpdate.UpdateBits.ORDER_BOOK
        )
        await ws.send(rq.SerializeToString())

    async def stream(self):
        while True:
            try:
                async with websockets.connect(
                    self.config.websocket_url,
                    ping_interval=None,
                    open_timeout=15,
                    close_timeout=5,
                    max_size=None,
                ) as ws:
                    heartbeat_seconds = await self._login(ws)
                    symbol, exchange = await self._front_month(ws)
                    await self._subscribe(ws, symbol, exchange)
                    while True:
                        try:
                            raw = await asyncio.wait_for(
                                ws.recv(), timeout=max(1, heartbeat_seconds)
                            )
                        except asyncio.TimeoutError:
                            await self._heartbeat(ws)
                            continue

                        base = self.base.Base()
                        base.ParseFromString(raw)
                        if base.template_id == 101:
                            rp = self.market_response_pb.ResponseMarketDataUpdate()
                            rp.ParseFromString(raw)
                            if rp.rp_code and rp.rp_code[0] != "0":
                                raise RuntimeError(
                                    f"Market-data subscription rejected: {list(rp.rp_code)}"
                                )
                        elif base.template_id == 150:
                            msg = self.last_trade_pb.LastTrade()
                            msg.ParseFromString(raw)
                            aggressor = (
                                "buy"
                                if msg.aggressor
                                == self.last_trade_pb.LastTrade.TransactionType.BUY
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
                        elif base.template_id == 156:
                            msg = self.order_book_pb.OrderBook()
                            msg.ParseFromString(raw)
                            observed_at = datetime.fromtimestamp(
                                msg.ssboe + msg.usecs / 1_000_000, tz=UTC
                            )
                            for level, (price, size) in enumerate(
                                zip(msg.bid_price, msg.bid_size_64, strict=False), start=1
                            ):
                                yield normalize_depth(
                                    symbol=msg.symbol,
                                    observed_at=observed_at,
                                    price=Decimal(str(price)),
                                    size=Decimal(size),
                                    side="bid",
                                    level=level,
                                )
                            for level, (price, size) in enumerate(
                                zip(msg.ask_price, msg.ask_size_64, strict=False), start=1
                            ):
                                yield normalize_depth(
                                    symbol=msg.symbol,
                                    observed_at=observed_at,
                                    price=Decimal(str(price)),
                                    size=Decimal(size),
                                    side="ask",
                                    level=level,
                                )
            except asyncio.CancelledError:
                raise
            except Exception:
                # Fail transiently, then reconnect. Persistent auth/entitlement errors
                # remain visible to the supervisor through repeated health failures.
                await asyncio.sleep(5)
