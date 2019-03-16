# python-binance-api
A Python 2/3 client for the Binance REST and WebSocket APIs  https://github.com/binance-exchange/binance-official-api-docs

python-binance-api return an object that parsed from `json` for each method, set `return_json=True` get the original API response.

#### Installation
```
download latest release from https://github.com/unicorn-data-analysis/python-binance-api/releases and put the binance directory into your project...
```
#### Requires
  * requests
  * simplejson
  * six
  * websocket-client
  * Events
 
#### Getting started
```python
from binance.client import BinanceRESTAPI, BinanceWebSocketAPI

rest_client = BinanceRESTAPI(api_key, secret_key)
ws_client = BinanceWebSocketAPI(api_key)
```

#### Ping
```python
rest_client.ping()
```

#### server time
```python
rest_client.server_time().server_time

# return json
rest_client.server_time(return_json=True)["serverTime"]
```

#### depth
```python
depth = rest_client.depth("BNBBTC")

# total voulme
depth.get_depth_volume()

# best bid price
depth.get_bids_highest_price()

# best ask price
depth.get_asks_lowest_price()
```

#### aggregate trades 
```python
rest_client.aggregate_trades(symbol="BNBBTC")

agg_trades = rest_client.aggregate_trades("BNBBTC")

for agg_trade in agg_trades:
    print agg_trade.id, agg_trade.price, agg_trade.qty
```

#### klines
```python
rest_client.klines("BNBBTC", "1w")

klines = rest_client.klines(symbol="BNBBTC", interval="1w")

for kline in klines:
    print kline.open_time, kline.close_time, kline.high, kline.volume
```

#### 24hr ticker price change statistics
```python
pre_day = rest_client.statistics_24hr("BNBBTC")

print pre_day.price_change_percent, pre_day.high_price
```

#### latest price for all symbols.
```python
prices = rest_client.all_prices()

for price in prices:
    print price.symbol, price.price
```

#### best price/qty on the order book for all symbols.
```python
tickers = rest_client.all_book_tickers()

for ticker in tickers:
    print ticker.symbol, ticker.bid.price, ticker.bid.qty
```

#### send in a new order
```python
order = rest_client.new_order("SNMBTC", "SELL", "LIMIT", "GTC", 1, '1')

# order id
print order.id
```

#### test new order creation
```python
rest_client.new_order_test(symbol="SNMBTC", side="SELL", type="LIMIT", time_in_force="GTC", quantity=1, price=1)
```

#### check an order's status.
```python
order = rest_client.query_order(symbol="SNMBTC", order_id=order.id, orig_client_order_id=order.client_order_id)

print order.status, order.type
```

#### cancel an active order
```python
order = rest_client.cancel_order("SNMBTC", order.id, order.client_order_id)

print order.id
```

#### get all open orders on a symbol
```python
orders = rest_client.current_open_orders("SNMBTC")

for order in orders:
    print order.id, order.status, order.side
```

#### get all account orders; active, canceled, or filled
```python
orders = rest_client.all_orders(symbol="SNMBTC")

for order in orders:
    print order.id, order.status, order.side
```

#### get current account information
```python
account = rest_client.account()

# balance information
for balance in account.balances:
    print balance.asset, balance.free, balance.locked
```

#### get trades for a specific account and symbol
```python
trades = rest_client.my_trades("BNBBTC")

for trade in trades:
    print trade.id, trade.price, trade.qty
```

#### submit a withdraw request
```python
withdraw = rest_client.withdraw(asset="BNB", address="address", amount=0.1, name="test")

print withdraw.success
```

#### fetch deposit history
```python
deposit_history = rest_client.deposit_history()

for deposit in deposit_history:
    print deposit.asset, deposit.amount, deposit.insert_time, deposit.status
```

#### fetch withdraw history
```python
withdraw_history = rest_client.withdraw_history()

for withdraw in withdraw_history:
    print withdraw.asset, withdraw.address, withdraw.amount, withdraw.apply_time, withdraw.status
```

#### start a new user data stream
```python
stream = rest_client.start_user_data_stream()

print stream.listen_key
```

#### PING a user data stream to prevent a time out
```python
rest_client.keepalive_user_data_stream(stream.listen_key)
```

#### close out a user data stream
```python
rest_client.close_user_data_stream(stream.listen_key)
```

#### WebSocket for depth
```python
from binance.models import DepthCache

# keep a depth cache
depth_cache = DepthCache(rest_client.depth("BNBBTC"))

def on_update(delta):
    depth_cache.update(delta)
    for bid in depth_cache.bids:
        print bid.price, bid.qty
    
ws_client.depth("BNBBTC", callback=on_update)
```

#### WebSocket for kline
```python
def on_print(kline):
    print kline.event_time, kline.open, kline.high, kline.is_final

ws_client.kline("ETHBTC", "1m", callback=on_print)
```

#### WebSocket for trades
```python
def on_print(trade):
    print trade.symbol, trade.price, trade.qty

ws_client.aggregate_trade("ETHBTC", callback=on_print)
```

#### WebSocket for user data
```python
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
```
