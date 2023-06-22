import logging
import time

from base_trade import BaseTrade
from kucoin.client import Trade

from bot_log import BotLog
from exchanges.kucoin.kucoin_exception import KucoinAPIException


class KucoinTrade(BaseTrade):
    def __init__(self, config, get_data_function=None, rest_update_function=None):
        super().__init__(config)
        
        self.log = logging.getLogger("KucoinTrade")
        self.log.setLevel(config["log_level"])
        
        if callable(get_data_function):
            self._get_data = get_data_function

        if callable(get_data_function):
            self._rest_update = rest_update_function

        self._exchange = "Kucoin"
        self._account_type = config["account_type"]
        self._trade = Trade(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"],
            is_sandbox=(config["sandbox"] == "True")
        )

    def create_limit_margin_order(self, symbol, side, size, price, clientOid='', **kwargs):
        try:
            results = self._trade.create_limit_margin_order(symbol, side, size, price, clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating limit margin order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating limit margin order: {ex}")
        return None

    def create_market_margin_order(self, symbol, side, clientOid='', **kwargs):
        try:
            results = self._trade.create_market_margin_order(symbol, side, clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating market margin order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating market margin order: {ex}")
        return None

    def create_limit_order(self, symbol, side, size, price, clientOid='', **kwargs):
        try:
            results = self._trade.create_limit_order(symbol, side, size, price, clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating limit order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating limit order: {ex}")
        return None

    def create_limit_stop_order(self, symbol, side, size, price, stopPrice,  clientOid="", **kwargs):
        try:
            results = self._trade.create_limit_stop_order(symbol, side, size, price, stopPrice,  clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating limit stop order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating limit stop order: {ex}")
        return None

    def create_market_stop_order(self, symbol, side, stopPrice, size="", funds="", clientOid="", **kwargs):
        try:
            results = self._trade.create_market_stop_order(symbol, side, stopPrice, size, funds, clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating market stop order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating market stop order: {ex}")
        return None

    def create_market_order(self, symbol, side, clientOid='', **kwargs):
        try:
            results = self._trade.create_market_order(symbol, side, clientOid, **kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating market order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating market order: {ex}")
        return None

    def create_bulk_orders(self, symbol, orderList):
        try:
            results = self._trade.create_bulk_orders(symbol, orderList)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error creating bulk orders: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error creating bulk orders: {ex}")
        return None

    def cancel_client_order(self, clientId):
        try:
            results = self._trade.cancel_client_order(clientId)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling client order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling client order: {ex}")
        return None

    def cancel_stop_order(self, orderId):
        try:
            results = self._trade.cancel_stop_order(orderId)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling stop order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling stop order: {ex}")
        return None

    def cancel_client_stop_order(self, orderId, symbol=""):
        try:
            results = self._trade.cancel_client_stop_order(orderId, symbol)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling client stop order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling client stop order: {ex}")
        return None

    def cancel_stop_condition_order(self, symbol="", tradeType="", orderIds=""):
        try:
            results = self._trade.cancel_stop_condition_order(symbol, tradeType, orderIds)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling stop condition order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling stop condition order: {ex}")
        return None

    def cancel_order(self, **kwargs):
        try:
            results = self._trade.cancel_order(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling order: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling order: {ex}")
        return None

    def cancel_all_orders(self, **kwargs):
        try:
            results = self._trade.cancel_all_orders(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error canceling all orders: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error canceling all orders: {ex}")
        return None

    def get_order_list(self, **kwargs):
        try:
            acc_type = str(self._account_type).upper()
            if acc_type == "MARGIN" or "MARGIN_ISOLATED":
                acc_type = acc_type + "_TRADE"
            kwargs = {
                "symbol": self.get_trade_symbol(),
                "tradeType": acc_type
            }
            results = self._trade.get_order_list(**kwargs)
            if "items" in results and len(results["items"]) > 0:
                # update the data store with the order history
                cache_object = {
                    "topic": "tradeOrders",
                    "data": results["items"]
                }
                self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting order list: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting order list: {ex}")
        return None

    def get_recent_orders(self):
        try:
            results = self._trade.get_recent_orders()
            if isinstance(list) and len(results) > 0:
                cache_object = {
                    "topic": "tradeOrders",
                    "data": results["items"]
                }
                self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting recent orders: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting recent orders: {ex}")
        return None

    def get_order_details(self, orderId):
        try:
            results = self._trade.get_order_details(orderId)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting order details: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting order details: {ex}")
        return None

    def get_all_stop_order_details(self, **kwargs):
        try:
            results = self._trade.get_all_stop_order_details(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting all stop order details: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting all stop order details: {ex}")
        return None

    def get_stop_order_details(self, **kwargs):
        try:
            results = self._trade.get_stop_order_details(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting stop order details: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting stop order details: {ex}")
        return None

    def get_client_stop_order_details(self, clientOid, symbol=''):
        try:
            results = self._trade.get_client_stop_order_details(clientOid, symbol)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting client stop order details: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting client stop order details: {ex}")
        return None

    def get_fill_list(self, tradeType, **kwargs):
        if tradeType == "spot":
            tradeType = "TRADE"
        elif tradeType == "margin":
            tradeType = "MARGIN_TRADE"
        else:
            logging.getLogger().error("invalid trade type in get_fills_list")
            return None

        try:
            results = self._trade.get_fill_list(tradeType, **kwargs)
            if "items" in results and len(results["items"]) > 0:
                cache_object = {
                    "topic": "fills",
                    "data": results["items"]
                }
                self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting fill list: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting fill list: {ex}")
        return None

    def get_recent_fills(self):
        try:
            results = self._trade.get_recent_fills()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting recent fills: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting recent fills: {ex}")
        return None

    def get_client_order_details(self, clientOid):
        try:
            results = self._trade.get_client_order_details(clientOid)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting client order details: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting client order details: {ex}")
        return None

    def initialize(self):
        self.get_order_list()
        self.get_fill_list(self._account_type)
        time.sleep(1)