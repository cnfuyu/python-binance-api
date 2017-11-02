#!/usr/bin/env python
# coding=utf-8

import six

def camel_to_underline(camel_format):
    underline_format=''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_'+_s_.lower()
    return underline_format

def sort_dict_in_list(data, sort_key, reverse=False):
    return sorted(data, key=lambda k: getattr(k, sort_key), reverse=reverse)

class ApiModel(object):
    
    @classmethod
    def object_from_dictionary(cls, entry):
        if entry is None:
            return ""
        entry_str_dict = dict([(camel_to_underline(str(key)), value) for key, value in entry.items()])
        return cls(**entry_str_dict)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        else:
            return unicode(self).encode('utf-8')

class Entry(ApiModel):
    def __init__(self, *args, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __unicode__(self):
        return "Entry"

class Bid(ApiModel):

    def __init__(self, price, qty):
        self.price = price
        self.qty = qty

    @classmethod
    def object_from_dictionary(cls, array):
        new_bid = Bid(array[0], array[1])
        return new_bid

    def __unicode__(self):
        return "Bid: (%s, %s)" % (self.price, self.qty)
    
class Ask(ApiModel):
    def __init__(self, price, qty):
        self.price = price
        self.qty = qty

    @classmethod
    def object_from_dictionary(cls, array):
        new_ask = Ask(array[0], array[1])
        return new_ask

    def __unicode__(self):
        return "Ask: (%s, %s)" % (self.price, self.qty)

class Depth(ApiModel):

    def __init__(self, last_update_id=None, bids=None, asks=None):
        self.last_update_id = last_update_id
        if bids != None: self.bids = sort_dict_in_list(bids, "price", reverse=True)
        if asks != None: self.asks = sort_dict_in_list(asks, "price")

    def _get_volume(self, data):
        volume = {
            "base": 0.0,
            "qty": 0.0,
        }

        for d in data:
            volume["base"] = volume["base"] + float(d.price) * float(d.qty)
            volume["qty"] = volume["qty"] + float(d.qty)

        volume["base"] = round(volume["base"], 8)
        volume["qty"] = round(volume["qty"], 8)
        return volume

    def get_depth_volume(self):
        volume = {}
        volume["bids"] = self._get_volume(self.bids)
        volume["asks"] = self._get_volume(self.asks)
        return volume

    def get_bids_highest_price(self):
        return self.bids[0].price

    def get_asks_lowest_price(self):
        return self.asks[0].price

    @classmethod
    def object_from_dictionary(cls, entry):
        new_depth = Depth(last_update_id=entry["lastUpdateId"])
        new_depth.bids = []
        new_depth.asks = []
        
        if "bids" in entry:
            for bid in entry["bids"]:
                new_depth.bids.append(Bid.object_from_dictionary(bid))
            new_depth.bids = sort_dict_in_list(new_depth.bids, "price", reverse=True)

        if "asks" in entry:
            for ask in entry["asks"]:
                new_depth.asks.append(Ask.object_from_dictionary(ask))
            new_depth.asks = sort_dict_in_list(new_depth.asks, "price")

        return new_depth

    def __unicode__(self):
        return "Depth: %s" % self.last_update_id

class DepthCache(object):
    def __init__(self, depth):
        self.last_update_id = depth.last_update_id
        self.bids = {}
        self.asks = {}
        for bid in depth.bids:
            self.bids[bid.price] = bid.qty

        for ask in depth.asks:
            self.asks[ask.price] = ask.qty

    def update_bid(self, bid):
        self.bids[bid.price] = bid.qty
        if bid.qty == "0.00000000": 
            del self.bids[bid.price]

    def update_ask(self, ask):
        self.asks[ask.price] = ask.qty
        if ask.qty == "0.00000000": 
            del self.asks[ask.price]

    def update(self, delta):
        if delta.update_id > self.last_update_id:
            self.last_update_id = delta.update_id
            for bid in delta.bids: self.update_bid(bid)
            for ask in delta.asks: self.update_ask(ask)

    def __unicode__(self):
        return "DepthCache: %s" % self.last_update_id

    def __repr__(self):
        return str(self)

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        else:
            return unicode(self).encode('utf-8')

class Trade(ApiModel):
    def __init__(self, id=None, **kwargs):
        self.id = id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __unicode__(self):
        return "Trade: %s" % self.id

class AggregateTrade(ApiModel):
    def __init__(self, id=None, **kwargs):
        self.id = id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_aggregate_trade = AggregateTrade(id=entry["a"])

        new_aggregate_trade.price = entry["p"]
        new_aggregate_trade.qty = entry["q"]
        new_aggregate_trade.first_trade_id = entry["f"]
        new_aggregate_trade.last_trade_id = entry["l"]
        new_aggregate_trade.timestamp = entry["T"]
        new_aggregate_trade.is_maker = entry["m"]
        new_aggregate_trade.is_best_match = entry["M"]

        return new_aggregate_trade

    def __unicode__(self):
        return "AggregateTrade: %s" % self.id

class Candlestick(ApiModel):
    def __init__(self, open_time, close_time, **kwargs):
        self.open_time = open_time
        self.close_time = close_time
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_candlestick = Candlestick(open_time=entry[0], close_time=entry[6])
        
        new_candlestick.open = entry[1]
        new_candlestick.high = entry[2]
        new_candlestick.low = entry[3]
        new_candlestick.close = entry[4]
        new_candlestick.volume = entry[5]
        new_candlestick.quote_asset_volume = entry[7]
        new_candlestick.number_of_trades = entry[8]
        new_candlestick.base_asset_volume = entry[9]
        new_candlestick.quote_asset_volume = entry[10]

        return new_candlestick

    def __unicode__(self):
        return "Candlestick: %s-%s" % (self.open_time, self.close_time)

class Statistics(ApiModel):
    def __init__(self, first_id, last_id, **kwargs):
        self.first_id = first_id
        self.last_id = last_id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_statistics = Statistics(entry["firstId"], entry["lastId"])

        for key, value in six.iteritems(entry):
            setattr(new_statistics, camel_to_underline(str(key)), value)

        return new_statistics

    def __unicode__(self):
        return "Statistics: %s-%s" % (self.first_id, self.last_id)

class Price(ApiModel):
    def __init__(self, price, **kwargs):
        self.price = price
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_price = Price(entry["price"])
        new_price.symbol = entry["symbol"]

        return new_price

    def __unicode__(self):
        return "Price: %s(%s)" % (self.symbol, self.price)

class Ticker(ApiModel):
    def __init__(self, symbol, **kwargs):
        self.symbol = symbol
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_ticker = Ticker(entry["symbol"])
        new_ticker.bid = Bid(entry["bidPrice"], entry["bidQty"])
        new_ticker.ask = Ask(entry["askPrice"], entry["askQty"])

        return new_ticker

    def __unicode__(self):
        return "Ticker: %s" % self.symbol

class Order(ApiModel):
    def __init__(self, id, **kwargs):
        self.id = id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)
    
    @classmethod
    def object_from_dictionary(cls, entry):
        new_order = Order(entry["orderId"])
        
        for key, value in six.iteritems(entry):
            setattr(new_order, camel_to_underline(str(key)), value)

        return new_order

    def __unicode__(self):
        return "Order: %s" % self.id

class Balance(ApiModel):
    def __init__(self, asset, free, locked, **kwargs):
        self.asset = asset
        self.free = free
        self.locked = locked
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __unicode__(self):
        return "Balance: %s" % self.asset

class Account(ApiModel):
    def __init__(self, *args, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def balances_dict(self):
        return dict([(balance["asset"], balance) for balance in self.balances])

    @classmethod
    def object_from_dictionary(cls, entry):
        new_account = Account()
        
        for key, value in six.iteritems(entry):
            setattr(new_account, camel_to_underline(str(key)), value)

        new_account.balances = []
        new_account.balances_dict = {}
        for balance in entry["balances"]:
            new_account.balances.append(Balance.object_from_dictionary(balance))

        return new_account

    def __unicode__(self):
        return "Account"

class Deposit(ApiModel):
    def __init__(self, *args, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        deposit_list = []
        for deposit in entry["depositList"]:
            new_deposit = Deposit()
            new_deposit.insert_time = deposit["insertTime"]
            new_deposit.amount = deposit["amount"]
            new_deposit.asset = deposit["asset"]
            new_deposit.status = deposit["status"]
            deposit_list.append(new_deposit)
        return deposit_list

    def __unicode__(self):
        return "Deposit"

class Withdraw(ApiModel):
    def __init__(self, *args, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        withdraw_list = []
        for withdraw in entry["withdrawList"]:
            new_withdraw = WithDraw()
            new_withdraw.amount = withdraw["amount"]
            new_withdraw.address = withdraw["address"]
            new_withdraw.asset = withdraw["asset"]
            new_withdraw.apply_time = withdraw["applyTime"]
            new_withdraw.status = withdraw["status"]
            withdraw_list.append(new_withdraw)
        return withdraw_list

    def __unicode__(self):
        return "Withdraw"

class DepthUpdateEvent(ApiModel):
    EVENT_TYPE = "depthUpdate" 

    def __init__(self, update_id, **kwargs):
        self.update_id = update_id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_depth_delta = DepthUpdateEvent(entry["u"])

        new_depth_delta.event_type = entry["e"]
        new_depth_delta.event_time = entry["E"]
        new_depth_delta.symbol = entry["s"]
        new_depth_delta.bids = []
        new_depth_delta.asks = []

        for bid in entry["b"]:
            new_depth_delta.bids.append(Bid.object_from_dictionary(bid))

        for ask in entry["a"]:
            new_depth_delta.asks.append(Ask.object_from_dictionary(ask))

        return new_depth_delta

    def __unicode__(self):
        return "DepthDeltaEvent: %s" % self.update_id

class KLineEvent(ApiModel):
    EVENT_TYPE = "kline" 

    def __init__(self, start_time, end_time, **kwargs):
        self.start_time = start_time
        self.end_time = end_time
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_kline = KLineEvent(entry["k"]["t"], entry["k"]["T"])

        new_kline.event_type = entry["e"]
        new_kline.event_time = entry["E"]
        entry = entry["k"]
        new_kline.symbol = entry["s"]
        new_kline.interval = entry["i"]
        new_kline.first_trade_id = entry["f"]
        new_kline.last_trade_id = entry["L"]
        new_kline.open = entry["o"]
        new_kline.close = entry["c"]
        new_kline.high = entry["h"]
        new_kline.low = entry["l"]
        new_kline.volume = entry["v"]
        new_kline.number_of_trades = entry["n"]
        new_kline.is_final = entry["x"]
        new_kline.quote_volume = entry["q"]
        new_kline.active_buy_volume = entry["V"]
        new_kline.active_buy_quote_volume = entry["Q"]

        return new_kline

    def __unicode__(self):
        return "KLineEvent: %s-%s" % (self.start_time, self.end_time)

class AggregateTradeEvent(ApiModel):
    EVENT_TYPE = "aggTrade" 

    def __init__(self, event_time, **kwargs):
        self.event_time = event_time
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_aggregate_trade = AggregateTradeEvent(event_time=entry["E"])

        new_aggregate_trade.event_type = entry["e"]
        new_aggregate_trade.symbol = entry["s"]
        new_aggregate_trade.price = entry["p"]
        new_aggregate_trade.qty = entry["q"]
        new_aggregate_trade.first_breakdown_trade_id = entry["f"]
        new_aggregate_trade.last_breakdown_trade_id = entry["l"]
        new_aggregate_trade.trade_time = entry["T"]
        new_aggregate_trade.is_maker = entry["m"]

        return new_aggregate_trade

    def __unicode__(self):
        return "AggregateTradeEvent: %s" % self.event_time

class OutBoundAccountInfoEvent(ApiModel):
    EVENT_TYPE = "outboundAccountInfo" 

    def __init__(self, event_time, **kwargs):
        self.event_time = event_time
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_event = OutBoundAccountInfoEvent(event_time=entry["E"])

        new_event.event_type = entry["e"]
        new_event.balances = []
        for balance in entry["B"]:
            new_event.balances.append(Balance(balance["a"], balance["f"], balance["l"]))

        return new_event

    def __unicode__(self):
        return "OutBoundAccountInfoEvent: %s" % self.event_time

class ExecutionReportEvent(ApiModel):
    EVENT_TYPE = "executionReport" 

    def __init__(self, event_time, **kwargs):
        self.event_time = event_time
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        new_event = ExecutionReportEvent(event_time=entry["E"])

        new_event.event_type = entry["e"]
        new_event.symbol = entry["s"]
        new_event.new_client_order_id = entry["c"]
        new_event.side = entry["S"]
        new_event.order_type = entry["o"]
        new_event.time_in_force = entry["f"]
        new_event.original_quantity = entry["q"]
        new_event.price = entry["p"]
        new_event.execution_type = entry["x"]
        new_event.order_status = entry["X"]
        new_event.order_reject_reason = entry["r"]
        new_event.order_id = entry["i"]
        new_event.last_filled_trade_quantity = entry["l"]
        new_event.filled_trade_accumulated_quantity = entry["z"]
        new_event.last_filled_trade_price = entry["L"]
        new_event.commission = entry["n"]
        new_event.commission_asset = entry["N"]
        new_event.order_time = entry["T"]
        new_event.trade_time = entry["T"]
        new_event.trade_id = entry["t"]
        new_event.is_maker = entry["m"]

        return new_event

    def __unicode__(self):
        return "ExecutionReportEvent: %s" % self.event_time 

class UserDataEvent(object):

    @classmethod
    def object_from_dictionary(cls, entry):
        if entry["e"] == OutBoundAccountInfoEvent.EVENT_TYPE:
            return OutBoundAccountInfoEvent.object_from_dictionary(entry)
        elif entry["e"] == ExecutionReportEvent.EVENT_TYPE:
            return ExecutionReportEvent.object_from_dictionary(entry)
