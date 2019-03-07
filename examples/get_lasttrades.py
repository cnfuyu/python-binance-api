#!/usr/bin/env python
# coding=utf-8

from binance.client import BinanceRESTAPI, BinanceWebSocketAPI

api_key = "YOUR API KEY"
secret_key = "YOUR SECRET KEY"

#---------------------------REST API Examples---------------------------

rest_client = BinanceRESTAPI(api_key, secret_key)

# ping
rest_client.ping()

# server time
server_time = rest_client.server_time()

# aggregate trades
rest_client.aggregate_trades(symbol="BNBBTC")

agg_trades = rest_client.aggregate_trades("BNBBTC")

for agg_trade in agg_trades:
    print(agg_trade.id, agg_trade.price, agg_trade.qty)
# start a new user data stream
stream = rest_client.start_user_data_stream()

print(stream.listen_key)

# PING a user data stream to prevent a time out
rest_client.keepalive_user_data_stream(stream.listen_key)

# close out a user data stream
rest_client.close_user_data_stream(stream.listen_key)



ws_client = BinanceWebSocketAPI(api_key)

# WebSocket for trades
def on_print(trade):
    print(trade.symbol, trade.price, trade.qty)

ws_client.aggregate_trade("ETHBTC", callback=on_print)

ws_client.user_data_keepalive(callback=on_print)
