#!/usr/bin/env python
# coding=utf-8

import time
import six

if six.PY3:
    import _thread as thread
else:
    import thread

from .bind import bind_method, bind_ws_method
from .models import Entry, Depth, Trade, AggregateTrade, Candlestick, Statistics, Price, Ticker, Order, Account, \
                    Deposit, Withdraw, DepthUpdateEvent, KLineEvent, AggregateTradeEvent, UserDataEvent

NO_ACCEPT_PARAMETERS = []

class BinanceRESTAPI(object):
    host = "www.binance.com"
    base_path = "/api"
    wapi_base_path = "/wapi"
    protocol = "https"
    api_name = "Binance"

    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key

    ping = bind_method(
            path="/v1/ping",
            method="GET",
            accepts_parameters=NO_ACCEPT_PARAMETERS,
            response_type="empty")

    server_time = bind_method(
            path="/v1/time",
            method="GET",
            accepts_parameters=NO_ACCEPT_PARAMETERS,
            response_type="entry",
            root_class=Entry)

    depth = bind_method(
            path="/v1/depth",
            method="GET",
            accepts_parameters=["symbol", "limit"],
            response_type="entry",
            root_class=Depth)

    aggregate_trades = bind_method(
            path="/v1/aggTrades",
            method="GET",
            accepts_parameters=["symbol", "from_id", "start_time", "end_time", "limit"],
            response_type="list",
            root_class=AggregateTrade)

    klines = bind_method(
            path="/v1/klines",
            method="GET",
            accepts_parameters=["symbol", "interval", "limit", "start_time", "end_time"],
            response_type="list",
            root_class=Candlestick)

    statistics_24hr = bind_method( 
            path="/v1/ticker/24hr",
            method="GET",
            accepts_parameters=["symbol"],
            response_type="entry",
            root_class=Statistics)

    all_prices = bind_method(
            path="/v1/ticker/allPrices",
            method="GET",
            accepts_parameters=NO_ACCEPT_PARAMETERS,
            response_type="list",
            root_class=Price)

    all_book_tickers = bind_method(
            path="/v1/ticker/allBookTickers",
            method="GET",
            accepts_parameters=NO_ACCEPT_PARAMETERS,
            response_type="list",
            root_class=Ticker)

    new_order = bind_method(
            path="/v3/order",
            method="POST",
            accepts_parameters=["symbol", "side", "type", "time_in_force", "quantity", "price", "new_client_order_id", "stop_price", "iceberg_qty", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Order)

    new_order_test = bind_method(
            path="/v3/order/test",
            method="POST",
            accepts_parameters=["symbol", "side", "type", "time_in_force", "quantity", "price", "new_client_order_id", "stop_price", "iceberg_qty", "recv_window", "timestamp"],
            signature=True,
            response_type="empty")

    query_order = bind_method(
            path="/v3/order",
            method="GET",
            accepts_parameters=["symbol", "order_id", "orig_client_order_id", "recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Order)

    cancel_order = bind_method(
            path="/v3/order",
            method="DELETE",
            accepts_parameters=["symbol", "order_id", "orig_client_order_id", "new_client_order_id", "recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Order)

    current_open_orders = bind_method(
            path="/v3/openOrders",
            method="GET",
            accepts_parameters=["symbol", "recv_window", "timestamp"],
            signature=True,
            response_type="list",
            root_class=Order)

    all_orders = bind_method(
            path="/v3/allOrders",
            method="GET",
            accepts_parameters=["symbol", "order_id", "limit", "recv_window", "timestamp"],
            signature=True,
            response_type="list",
            root_class=Order)

    account = bind_method(
            path="/v3/account",
            method="GET",
            accepts_parameters=["recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Account)

    my_trades = bind_method(
            path="/v3/myTrades",
            method="GET",
            accepts_parameters=["symbol", "limit", "from_id", "recv_window", "timestamp"],
            signature=True,
            response_type="list",
            root_class=Trade)

    start_user_data_stream = bind_method(
            path="/v1/userDataStream",
            method="POST",
            accepts_parameters=NO_ACCEPT_PARAMETERS,
            api_key_required=True,
            response_type="entry",
            root_class=Entry)

    keepalive_user_data_stream = bind_method(
            path="/v1/userDataStream",
            method="PUT",
            accepts_parameters=["listen_key"],
            api_key_required=True,
            response_type="empty")

    close_user_data_stream = bind_method(
            path="/v1/userDataStream",
            method="DELETE",
            accepts_parameters=["listen_key"],
            api_key_required=True,
            response_type="empty")

    withdraw = bind_method(
            path="/v1/withdraw.html",
            method="POST",
            accepts_parameters=["asset", "address", "amount", "name", "recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Entry)

    deposit_history = bind_method(
            path="/v1/getDepositHistory.html",
            method="POST",
            accepts_parameters=["asset", "status", "start_time", "end_time", "recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Deposit)

    withdraw_history = bind_method(
            path="/v1/getWithdrawHistory.html",
            method="POST",
            accepts_parameters=["asset", "status", "start_time", "end_time", "recv_window", "timestamp"],
            signature=True,
            response_type="entry",
            root_class=Withdraw)

class BinanceWebSocketAPI(object):
    host = "stream.binance.com"
    port = "9443"
    protocol = "wss"
    base_path = "/ws"
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.rest_client = BinanceRESTAPI(self.api_key)
        self.depth_cache = Depth()

    depth = bind_ws_method(
            path="/{symbol}@depth",
            accepts_parameters=["symbol"],
            response_type="entry",
            root_class=DepthUpdateEvent)

    kline = bind_ws_method(
            path="/{symbol}@kline_{interval}",
            accepts_parameters=["symbol", "interval"],
            response_type="entry",
            root_class=KLineEvent)

    aggregate_trade = bind_ws_method(
            path="/{symbol}@aggTrade",
            accepts_parameters=["symbol"],
            response_type="entry",
            root_class=AggregateTradeEvent)

    user_data = bind_ws_method(
            path="/{listen_key}",
            accepts_parameters=["listen_key"],
            response_type="entry",
            root_class=UserDataEvent)

    def user_data_keepalive(self, *args, **kwargs):
        interval = kwargs.pop("keepalive_interval", 60)
        listen_key = self.rest_client.start_user_data_stream().listen_key

        def keepalive():
            while 1:
                self.rest_client.keepalive_user_data_stream(listen_key)
                time.sleep(interval)

        thread.start_new_thread(keepalive, ())

        return self.user_data(listen_key, *args, **kwargs)
