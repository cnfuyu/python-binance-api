#!/usr/bin/env python
# coding=utf-8

from binance.client import BinanceRESTAPI, BinanceWebSocketAPI
from binance.models import DepthCache

api_key = "YOUR API KEY"
secret_key = "YOUR SECRET KEY"

#---------------------------REST API Examples---------------------------

rest_client = BinanceRESTAPI(api_key, secret_key)

# ping
rest_client.ping()

# server time
server_time = rest_client.server_time()

# depth
depth = rest_client.depth(symbol="SNMBTC")

# total depth volume
depth.get_depth_volume() # output: {'bids': {'base': 44.53155962, 'qty': 5432314.0}, 'asks': {'base': 26.13383253, 'qty': 1287506.0}}

# best bid price
depth.get_bids_highest_price()

# best ask price
depth.get_asks_lowest_price()

# aggregate trades
rest_client.aggregate_trades(symbol="BNBBTC")

agg_trades = rest_client.aggregate_trades("BNBBTC")

for agg_trade in agg_trades:
    print agg_trade.id, agg_trade.price, agg_trade.qty

# klines
rest_client.klines("BNBBTC", "1w")

klines = rest_client.klines(symbol="BNBBTC", interval="1w")

for kline in klines:
    print kline.open_time, kline.close_time, kline.high, kline.volume

# 24hr ticker price change statistics
pre_day = rest_client.statistics_24hr("BNBBTC")

print pre_day.price_change_percent, pre_day.high_price

# latest price for all symbols.
prices = rest_client.all_prices()

for price in prices:
    print price.symbol, price.price

# best price/qty on the order book for all symbols
tickers = rest_client.all_book_tickers()

for ticker in tickers:
    print ticker.symbol, ticker.bid.price, ticker.bid.qty

# send in a new order
order = rest_client.new_order("SNMBTC", "SELL", "LIMIT", "GTC", 1, '1')

# order id
print order.id

# test new order creation
rest_client.new_order_test(symbol="SNMBTC", side="SELL", type="LIMIT", time_in_force="GTC", quantity=1, price=1)

# check an order's status.
order = rest_client.query_order(symbol="SNMBTC", order_id=order.id, orig_client_order_id=order.client_order_id)

print order.status, order.type

# cancel an active order
order = rest_client.cancel_order("SNMBTC", order.id, order.client_order_id)

print order.id

# get all open orders on a symbol
orders = rest_client.current_open_orders("SNMBTC")

for order in orders:
    print order.id, order.status, order.side

# get all account orders; active, canceled, or filled
orders = rest_client.all_orders(symbol="SNMBTC")

for order in orders:
    print order.id, order.status, order.side

# get current account information
account = rest_client.account()

# balance information
for balance in account.balances:
    print balance.asset, balance.free, balance.locked

# get trades for a specific account and symbol
trades = rest_client.my_trades("BNBBTC")

for trade in trades:
    print trade.id, trade.price, trade.qty

# start a new user data stream
stream = rest_client.start_user_data_stream()

print stream.listen_key

# PING a user data stream to prevent a time out
rest_client.keepalive_user_data_stream(stream.listen_key)

# close out a user data stream
rest_client.close_user_data_stream(stream.listen_key)


#---------------------------WebSocket API Examples---------------------------

ws_client = BinanceWebSocketAPI(api_key) 

# WebSocket for depth
from binance.models import DepthCache

depth_cache = DepthCache(rest_client.depth("BNBBTC"))

def on_update(delta):
    depth_cache.update(delta)
    for bid in depth_cache.bids:
        print bid.price, bid.qty
    
ws_client.depth("BNBBTC", callback=on_update)

# WebSocket for kline
def on_print(kline):
    print kline.event_time, kline.open, kline.high, kline.is_final

ws_client.kline("ETHBTC", "1m", callback=on_print)

# WebSocket for trades
def on_print(trade):
    print trade.symbol, trade.price, trade.qty

ws_client.aggregate_trade("ETHBTC", callback=on_print)

# WebSocket for user data
from binance.models import OutBoundAccountInfoEvent, ExecutionReportEvent

def on_print(data):
    if data.event_type == OutBoundAccountInfoEvent.EVENT_TYPE:
        for balance in data.balances:
            print balance.asset, balance.free, balance.locked
    elif data.event_type == ExecutionReportEvent.EVENT_TYPE:
        print data.symbol, data.side, data.price, data.original_quantity
 
ws_client.user_data_keepalive(callback=on_print)
 
# return json also available for WebSocket
def on_print(data):
    print data["e"]
   
ws_client.user_data_keepalive(callback=on_print, return_json=True)
