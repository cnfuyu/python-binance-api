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
print(depth.get_depth_volume()) # output: {'bids': {'base': 44.53155962, 'qty': 5432314.0}, 'asks': {'base': 26.13383253, 'qty': 1287506.0}}

# query aggregate trade with return json
agg_trade = rest_client.aggregate_trades(symbol="SNMBTC", return_json=True)
print(agg_trade[0]["a"]) # output: 53692

# klines
candlestick = rest_client.klines("SNMBTC", "1w")
print(candlestick[0].high) # output: 0.00021000

# query current open order with an objected return value
open_orders = rest_client.current_open_orders(symbol="SNMBTC", timestamp=server_time.server_time)
for order in open_orders:
    print(order.order_id, order.symbol, order.status) # output: 382545 SNMBTC NEW


#---------------------------WebSocket API Examples---------------------------

ws_client = BinanceWebSocketAPI(api_key) 

def on_print(data):
    print(data)
# user data with keepalive
ws_client.user_data_keepalive(callback=on_print, keepalive_interval=100) # keepalive_interval default is 60s

# keep a depth cache
depth_cache = DepthCache(rest_client.depth("BNBBTC"))
def on_update(update_data):
    print("Updating depth cache")
    depth_cache.update(update_data)
    print(depth.bids)
    print(depth_cache)
ws_client.depth("BNBBTC", callback=on_update)
