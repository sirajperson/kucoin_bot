import time
import logging
from base_market import BaseMarket
from kucoin.client import Market
from exchanges.kucoin.kucoin_exception import KucoinAPIException


class KucoinMarket(BaseMarket):
    def __init__(self, config, get_data_function=None, rest_update_function=None):
        super().__init__(config)
        self.log = logging.getLogger("KucoinMarket")
        self.log.setLevel(config["log_level"])

        self._time_delta = config["candle_length"]

        if callable(get_data_function):
            self._get_data = get_data_function

        if callable(get_data_function):
            self._rest_update = rest_update_function

        self._exchange = "Kucoin"
        self._market = Market(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"],
            is_sandbox=(config["sandbox"] == "True")
        )

    def get_fiat_price(self, **kwargs):
        try:
            results = self._market.get_fiat_price(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting fiat price: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting fiat price: {ex}")
        return None

    def get_all_tickers(self):
        try:
            results = self._market.get_all_tickers()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting all tickers: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting all tickers: {ex}")
        return None

    def get_kline(self, **kwargs):
        try:
            results = self._market.get_kline(self.get_trade_symbol(), self._time_delta, **kwargs)
            cache_object = {
                "topic": "candles",
                "data": {
                    "candles": results
                }
            }
            self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting kline for {self.get_trade_symbol()}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting kline for {self.get_trade_symbol()}: {ex}")
        return None

    def get_currency_detail_v2(self, currency, chain=None):
        try:
            results = self._market.get_currency_detail_v2(currency, chain)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting currency detail v2 for {currency}: {ex}")
        except Exception as ex:
            self.log.error(
                f"Unexpected error getting currency detail v2 for {currency}: {ex}")
        return None

    def get_atomic_order(self, symbol):
        try:
            results = self._market.get_atomic_order(symbol)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting atomic order for {symbol}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting atomic order for {symbol}: {ex}")
        return None

    def get_ticker(self, symbol):
        try:
            results = self._market.get_ticker(symbol)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting ticker for {symbol}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting ticker for {symbol}: {ex}")
        return None

    def get_atomic_orderv3(self, symbol):
        try:
            results = self._market.get_atomic_orderv3(symbol)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting atomic order v3 for {symbol}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting atomic order v3 for {symbol}: {ex}")
        return None

    def get_market_list(self):
        try:
            results = self._market.get_market_list()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting market list: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting market list: {ex}")
        return None

    def get_aggregated_orderv3(self):
        try:
            results = self._market.get_aggregated_orderv3(self.get_trade_symbol())
            results["asks"] = {float(price): float(size) for price, size in results["asks"]}
            results["bids"] = {float(price): float(size) for price, size in results["bids"]}


            cache_object = {
                "topic": "init_order_book",
                "results": results
            }
            self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting aggregated order v3 for {self.get_trade_symbol()}: {ex}")
        except Exception as ex:
            self.log.error(
                f"Unexpected error getting aggregated order v3 for {self.get_trade_symbol()}: {ex}")
        return None

    def get_currencies(self):
        try:
            results = self._market.get_currencies()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting currencies: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting currencies: {ex}")
        return None

    def get_server_timestamp(self):
        try:
            results = self._market.get_server_timestamp()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting server timestamp: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting server timestamp: {ex}")
        return None

    def get_currency_detail(self, currency, chain=None):
        try:
            self.log.warning("get_currency_detail is depreciated. Please update your code")
            results = self._market.get_currency_detail(currency, chain)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting currency detail for {currency}: {ex}")
        except Exception as ex:
            self.log.error(
                f"Unexpected error getting currency detail for {currency}: {ex}")
        return None

    def get_server_status(self):
        try:
            results = self._market.get_server_status()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting server status: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting server status: {ex}")
        return None

    def get_part_order(self, pieces, symbol):
        try:
            results = self._market.get_part_order(pieces, symbol)
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting part order for {symbol}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting part order for {symbol}: {ex}")
        return None

    def get_trade_histories(self, symbol):
        try:
            results = self._market.get_trade_histories(symbol)
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting trade histories for {symbol}: {ex}")
        except Exception as ex:
            self.log.error(f"Unexpected error getting trade histories for {symbol}: {ex}")
        return None

    def initialize(self):
        functions = [
            # self.get_all_tickers,
            # self.get_currencies,
            # self.get_market_list,
            # lambda: self.get_ticker(super().get_base_symbol()),
            # lambda: self.get_part_order(2, self.get_base_symbol()),
            # lambda: self.get_atomic_orderv3(self.get_base_symbol()),
            # lambda: self.get_atomic_order(self.get_base_symbol()),
            # lambda: self.get_trade_histories(self.get_base_symbol()),


            # lambda: self.get_currency_detail(super().get_base_symbol()),
            # self.get_fiat_price,
            # self.get_server_timestamp,
            # self.get_server_status
        ]

        # for i, function in enumerate(functions):
        #     print(function)
        #     function()
        #     if i % 3 == 2:  # Sleep after every 3rd call
        #         time.sleep(1)

        # self.get_currency_detail_v2(self.get_base_symbol())
        # self.get_currency_detail_v2(self.get_quote_symbol())
        time.sleep(1)
        self.get_kline()
        self.get_aggregated_orderv3()

    def ws_get_match_history(self):
        data = self._get_data()
        topic = "/market/match:" + self.get_trade_symbol()
        if topic in data:
            return data[topic]
        return None

    def ws_get_last_price(self):
        return self._get_data()["klines"][0][2]

    def ws_get_order_book(self):
        return self._get_data()["/market/level2:" + self.get_trade_symbol()]
