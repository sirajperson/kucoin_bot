import copy
import datetime
import logging
import os

import yaml

from base_exchange import BaseExchange
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient

from exchanges.kucoin.kucoin_trade import KucoinTrade
from exchanges.kucoin.kucoin_account import KucoinAccount
from exchanges.kucoin.kucoin_market import KucoinMarket
from exchanges.kucoin.kucoin_ta import KCTa
from check_config import Check as check

log = logging.getLogger("KucoinExchange")


def _check_config_file(config):
    check().config_file({
        "api_passphrase": "No 'api_passphrase' variable in the configuration file.",
        "log_level": "No 'api_secret' variable in the configuration file.",
        "candle_length": "No candle_length variable in the configuration file.",
        "sandbox": "No 'sandbox' variable in the configuration file."
    }, config)


class KucoinExchange(BaseExchange):
    _kc_cache = {}
    _MAX_TABLE_LENGTH = 200
    _send_ws_update = None
    _cache_initialized = False

    def __init__(self, config):
        _check_config_file(config)
        log.setLevel(config["log_level"])

        self._market = KucoinMarket(config, self._get_data, self._update_websocket_data_store)
        self._account = KucoinAccount(config, self._get_data, self._update_websocket_data_store)
        self._trade = KucoinTrade(config, self._get_data, self._update_websocket_data_store)
        self._ta = KCTa(config, self._get_data)
        self._time_delta = config["candle_length"]
        self._token = WsToken(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"],
            is_sandbox=(config["sandbox"] == "True"),
        )

        self._ws_client = None
        self._websocket_topics = [
            # Private channels.
            '/spotMarket/tradeOrders',
            '/account/balance',
            '/margin/position',
            # '/spotMarket/advancedOrders'

            # public channels
            # '/market/ticker:' + self.market().get_trade_symbol(),  # Push frequency: once every 100ms
            # '/market/snapshot:' + self.market().get_trade_symbol(),  # Push frequency: once every 2s
            # '/spotMarket/level2Depth5:' + self.market().get_trade_symbol(),  # Push frequency: once every 100ms
            '/market/candles:' + self.market().get_trade_symbol() + "_" + config["candle_length"],
            # Push frequency: real-time
            # '/indicator/index:' + self.market().get_market_symbol(),
            # '/market/match:' + self.market().get_trade_symbol(),  # Push frequency: real-time
            # '/indicator/markPrice:' + self.market().get_market_symbol(),
            # '/margin/fundingBook:' + self.market().get_base_symbol() + ',' + self.market().get_quote_symbol(),
            '/market/level2:' + self.market().get_trade_symbol(),  # Push frequency: real-time
        ]

        self._sequence = 0
        self._exchange = f"Kucoin {config['account_type']}"

        super().__init__(self)

    def account(self):
        return self._account

    def market(self):
        return self._market

    def trade(self):
        return self._trade

    def ta(self):
        return self._ta

    def initialize(self):
        log.debug("Initializing account data...")
        print("Initializing account data...")
        self.account().initialize()
        log.info("Initializing trade data...")
        print("Initializing trade data...")
        self.trade().initialize()
        log.info("Initializing market data...")
        print("Initializing market data...")
        self.market().initialize()
        log.info("Exchange information initialized!")
        print("Exchange information initialized!")
        self._cache_initialized = True
        return

    def _get_data(self):
        return self._kc_cache

    def ws_is_connected(self):
        return self._ws_client is not None

    def uninitialize_ws(self):
        self._ws_client = None

    def set_on_message(self, send_ws_update):
        self._send_ws_update = send_ws_update

    async def _receive_ws_message(self, ws_msg):
        result = self._update_websocket_data_store(ws_msg)

        if self._send_ws_update and result:
            self._send_ws_update(self._get_data(), ws_msg)

    ###### WEBSOCKET CLIENT ######
    async def connect_websocket_client(self):
        with open("configuration.yaml", "r") as file:
            config = yaml.safe_load(file)
        _check_config_file(config)

        ws_token = WsToken(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"]
        )

        # Create the handle_msg function with access to orderbook
        async def print_message(msg):
            print(msg)

        # Connect to WebSocket
        client = await KucoinWsClient.create(None,
                                             client=ws_token,
                                             callback=self._receive_ws_message,
                                             private=False)
        for topic in self._websocket_topics:
            await client.subscribe(topic)

        self._ws_client = client
        return True

    ####### WEBSOCKET FUNCTIONS #######
    def _update_websocket_data_store(self, message):
        log.debug(message)
        """
                Handles WebSocket messages to update the account data in real time.

                Args:
                    message (dict): A dictionary of message data.
                """
        if "topic" not in message:
            # This is an exchange REST result
            self._kc_cache = message
            return None

        if "/market/match" in message["topic"]:
            topic = message["topic"]
            if topic not in self._kc_cache:
                self._kc_cache[topic] = []
            self._kc_cache["topic"].append(message["data"])
            if len(self._kc_cache[topic]) > self._MAX_TABLE_LENGTH:
                del (self._kc_cache[topic][-1])
            return None

        if "/margin/position" in message["topic"]:
            topic = message["topic"]
            if topic not in self._kc_cache:
                self._kc_cache["/margin/position"] = {}

            self._kc_cache["/margin/position"] = message["data"]
            return 1

        if "init_order_book" in message["topic"]:
            self._initialize_order_book(message)
            return None

        if '/account/balance' in message['topic']:
            self.update_balances(message)
            return 1

        if "init_order_book" in message["topic"]:
            self._initialize_order_book(message)
            return None

        if "/market/level2" in message['topic']:
            topic = message['topic']
            if topic not in self._kc_cache:
                return None

            self.update_order_book(message)
            return 1

        if "candles" in message["topic"]:
            self.update_klines(message)
            return None

        if "tradeOrders" or "fills" in message['topic']:
            # if order_data['type'] in ['received', 'open', 'match', 'filled', 'canceled', 'update']:
            #     pass
            self.update_orders(message)
            return 1

    def update_balances(self, data=None):
        """
        Updates the balances dictionary using either provided data or the REST client.

        Args:
            data (dict): Optional; a dictionary of balance data.
        """
        if data:
            if "accounts" not in self._kc_cache:
                # Initializing the data_store
                self._kc_cache["accounts"] = {
                    self._market.get_market_type(): {
                        self._market.get_base_symbol(): {},
                        self._market.get_quote_symbol(): {}
                    }
                }

            if "data" not in data:
                # this is a REST message
                for currency in data["accounts"][self._market.get_market_type()]:
                    self._kc_cache["accounts"][self._market.get_market_type()][currency].update(
                        data["accounts"][self.market().get_market_type()][currency])
            else:
                # Update the balances dictionary using WebSocket data
                for balance in data:
                    if balance['currency'] not in self._kc_cache["accounts"]:
                        self._kc_cache["accounts"] = balance["currency"]

                    self._kc_cache[balance['currency']] = {
                        'available': float(balance['available']),
                        'holds': float(balance['holds'])
                    }
        else:

            # Fetch the current account balances using the REST client
            balances = self.exchange.account().get().balances()
            # if "accounts" not in self._web_socket_data_store:
            #     self._web_socket_data_store["accounts"] = balances["currency"]
            # # Update the balances dictionary
            # for balance in balances:
            #     self._web_socket_data_store[balance['currency']] = {
            #         'available': float(balance['available']),
            #         'holds': float(balance['holds'])
            #     }

    def _initialize_order_book(self, message):
        # Convert price and size values to floats
        orderbook = message["results"]
        self._kc_cache['/market/level2:' + self._market.get_trade_symbol()] = orderbook
        # self._print_market_book(orderbook, 13)
        return

    def update_order_book(self, data):
        # Update cache with new messages
        orderbook = self._kc_cache[data["topic"]]
        if not orderbook:
            return

        # Cache the changes data
        changes = data["data"]["changes"]

        # Apply the changes to the local order book
        for side in ["asks", "bids"]:
            if side in changes:
                for change in changes[side]:
                    price, size, sequence = change

                    # Convert price and size to float
                    price = float(price)
                    size = float(size)

                    if size == 0:
                        if price in orderbook[side]:
                            del orderbook[side][price]
                    else:
                        orderbook[side][price] = size

        # Update the sequence of the order book
        orderbook["sequence"] = data["data"]["sequenceEnd"]

    def update_orders(self, update_message=None):
        # Check to see if this is a received update or an update request
        topic = update_message["topic"]
        if topic == "fills":
            oKey = "orderId"
        else:
            oKey = "id"

        if not update_message:
            self.trade().get_order_list()
            return

        if "orders" not in self._kc_cache:
            # Initializing the data_store
            self._kc_cache["orders"] = {}

        for order in update_message["data"]:
            oid = order[oKey]
            if oid not in self._kc_cache["orders"]:
                self._kc_cache["orders"][oid] = order
            else:
                self._kc_cache["orders"][oid].update(order)
        return

    def get_snapshot(self):
        self._get_data()

    def update_klines(self, message=None):
        if "klines" not in self._kc_cache:
            self._kc_cache["klines"] = []

        if "subject" not in message:
            # This is a REST UPDATE
            # Convert the data types
            for candle in message["data"]["candles"]:
                # Explicitly convert the first value to int and the rest to float
                self._kc_cache["klines"].append([int(candle[0])] + [float(x) for x in candle[1:]])

        else:
            raw_update_candle = message["data"]["candles"]
            # Explicitly convert the first value to int and the rest to float
            update_candle = [int(raw_update_candle[0])] + [float(x) for x in raw_update_candle[1:]]

            if not self._kc_cache["klines"] or update_candle[0] > self._kc_cache["klines"][0][0]:
                # This is a new minute, insert the new candle at the top
                self._kc_cache["klines"].insert(0, update_candle)
                # Remove the last element if the length exceeds 100
                if len(self._kc_cache["klines"]) > 100:
                    self._kc_cache["klines"].pop()
            else:
                # This is the same minute, update the 0th element
                self._kc_cache["klines"][0] = update_candle

            # if len(self._kc_cache["klines"]) > self._MAX_TABLE_LENGTH:
            #     del (self._kc_cache["klines"][-1])
        return

    def _convert_length_to_delta(self, _time_delta):
        if _time_delta == "1min":
            return 1
        if _time_delta == "3min":
            return 3
        if _time_delta == "15min":
            return 15
        if _time_delta == "30min":
            return 30
        if _time_delta == "1hour":
            return 60
        if _time_delta == "2hour":
            return 60 * 2
        if _time_delta == "4hour":
            return 60 * 4
        if _time_delta == "6hour":
            return 60 * 6
        if _time_delta == "8hour":
            return 60 * 8
        if _time_delta == "12hour":
            return 60 * 12
        if _time_delta == "1day":
            return 60 * 24
        if _time_delta == "1week":
            return 60 * 24 * 7

        return None

    def unsubscribe(self):
        if self._ws_client:
            for topic in self._websocket_topics:
                self._ws_client.subscribe(topic)
