import os
import pandas as pd
import logging
from exchanges.kucoin.kucoin_exchange import KucoinExchange
from tabulate import tabulate


class TradingStrategy:
    def __init__(self, config, exchange):
        self._ws_data = None
        if not config:  # App Live
            SystemExit(BaseException("Wrong application entry point. Please run python main.py"))

        self._orderbook = None
        self.ta_list = None

        self.log = logging.getLogger("TradingStrategy")
        self.log.setLevel(config["log_level"])
        if not isinstance(exchange, KucoinExchange):
            raise TypeError("Exchange is wrong type.")
        self._exchange = exchange
        self.asset = config["asset"]
        self.order_volumes = config["order_volumes"]
        self.standard_deviations = config["order_levels"]
        self._exchange.set_on_message(self.receive_ws_update)

        self._s_length = int(config["sma_period"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    def initialize(self):
        self._exchange.initialize()

    def receive_ws_update(self, ws_data=None, msg=None):
        if self.not_initialized():
            return
        if not msg or "topic" not in msg:
            return

        if ws_data:
            self._ws_data = ws_data

        topic = msg['topic']
        data = msg['data']

        # Check if the message is a kline update
        if 'data' in msg and msg['type'] == 'message':

            if '/spotMarket/tradeOrdersV2' in topic:
                # Update strategy based on order event
                event_type = data['type']
                order_status = data["status"]

                # Check the type of the order event

                if event_type == 'received':
                    logging.info(f'Received new order {data}')

                elif event_type == 'done':
                    if order_status == 'cancelled':
                        logging.info(f'Order cancelled: {data}')

                        # Perform a strategy update when an order is cancelled.
                        # For example, you might want to place a new order here.
                        # self.update(event)

                    if order_status == 'filled' or order_status == 'matched':
                        logging.info(f'Order {data["orderId"]} has been {order_status}: {data}')

                        # Perform a strategy update when an order is filled.
                        # For example, you might want to place a new order here.
                        self.place_match_orders(data)

                elif event_type == 'open':
                    logging.info(f'Order {data["orderId"]} is open: {data}')

                else:
                    logging.warning(f'Unknown order event type: {event_type}')
        self.print_market_data()

    def not_initialized(self):
        return self._orderbook is None

    def update_market_data(self):
        self._orderbook = self._exchange.market().ws_get_order_book()
        _ochl = self._exchange.ta().get_ta()
        # Calculate the Bollinger Bands
        _bbands = _ochl.ta.bbands(close="close", length=self._s_length, std=2)
        # Reverse the DataFrames
        reversed_ochl = _ochl.round(2)
        reversed_bbands = _bbands.round(2)  # Round to 2 decimal places
        # Concatenate the DataFrames along the columns axis
        combined_df = pd.concat([reversed_ochl, reversed_bbands], axis=1)[::-1].head(25)

        combined_df.loc[:, 'open_time'] = pd.to_datetime(combined_df['open_time']).dt.strftime('%Y-%m-%d %H:%M')

        # Convert DataFrame to list of dictionaries for tabulation
        self.ta_list = combined_df.to_dict('records')
        return

    def print_market_data(self):
        # Only compute ta_list if it's None (i.e., the first time) or if the orderbook data has been updated
        if self.ta_list is None:
            self.update_market_data()
        # Get the asks and bids
        if self.not_initialized():
            return
        asks = sorted(self._orderbook['asks'].items())[:10]
        asks = asks[::-1]
        bids = sorted(self._orderbook['bids'].items(), reverse=True)[:10]

        # Convert 'bids' and 'asks' to list of dictionaries
        bids = [{'price': price, 'quantity': round(quantity, 4)} for price, quantity in bids]
        asks = [{'price': price, 'quantity': round(quantity, 4)} for price, quantity in asks]

        # Get the last price
        last_price = self._exchange.market().ws_get_last_price()

        # Format the tables
        ta_table = tabulate(self.ta_list, headers='keys', tablefmt='pretty').split('\n')  # use self.ta_list here
        bids_table = tabulate(bids, headers='keys', tablefmt='pretty').split('\n')
        asks_table = tabulate(asks, headers='keys', tablefmt='pretty').split('\n')

        # Insert the last price between asks and bids
        orderbook_table = asks_table + ['Last Price: ' + str(last_price)] + bids_table

        os.system('cls' if os.name == 'nt' else 'clear')
        # Print the tables side by side
        for line1, line2 in zip(ta_table, orderbook_table + [''] * (len(ta_table) - len(orderbook_table))):
            print(f'{line1}\t{line2}')
