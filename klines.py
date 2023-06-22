import asyncio
import datetime
import os

import yaml
from kucoin.client import Market, WsToken
from kucoin.ws_client import KucoinWsClient
from tabulate import tabulate

ob_depth = 13
# Fetch Initial Orderbook Data
with open("configuration.yaml", "r") as file:
    config = yaml.safe_load(file)

# Get WebSocket token
ws_token = WsToken(
    key=config["api_key"],
    secret=config["api_secret"],
    passphrase=config["api_passphrase"]
)


class OrderBook:
    def __init__(self):
        self.orderbook = None
        self.market = Market(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"])

    def update_orderbook(self, data):
        if not self.orderbook:
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
                        if price in self.orderbook[side]:
                            del self.orderbook[side][price]
                    else:
                        self.orderbook[side][price] = size

        # Update the sequence of the order book
        self.orderbook["sequence"] = data["data"]["sequenceEnd"]

    def initialize(self, symbol):
        self.orderbook = {'asks': {}, 'bids': {}}
        orderbook_snapshot = self.market.get_aggregated_orderv3(symbol)
        asks = {float(price): float(size) for price, size in orderbook_snapshot["asks"]}
        bids = {float(price): float(size) for price, size in orderbook_snapshot["bids"]}
        self.orderbook = {"asks": asks, "bids": bids}

    def print_orderbook(self, depth=10):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Get the asks
        asks = sorted(self.orderbook['asks'].items())[:depth]
        asks = asks[::-1]
        bids = sorted(self.orderbook['bids'].items(), reverse=True)[:depth]

        # Create a table with the asks
        asks_table = [['Price', 'Size']] + asks
        print("Asks:")
        print(tabulate(asks_table, headers='firstrow', tablefmt='pipe'))

        print("\n")

        # Create a table with the bids
        bids_table = [['Price', 'Size']] + bids
        print("Bids:")
        print(tabulate(bids_table, headers='firstrow', tablefmt='pipe'))


orderbook = OrderBook()


def create_handle_msg(update_ob):
    async def handle_msg(msg):
        # Process the WebSocket message
        if 'topic' in msg:
            data = msg['data']
            topic = msg['topic']

            if 'level2' in topic:
                changes = data['changes']

                # Update the orderbook
                update_ob.update_orderbook(msg)

                # Print the market book
                update_ob.print_orderbook(depth=ob_depth)
        else:
            print(f"Received message without 'topic' field: {msg}")

    return handle_msg

async def main():
    symbol = 'BTC-USDT'

    # Create the handle_msg function with access to orderbook
    handle_msg = create_handle_msg(orderbook)
    client = await KucoinWsClient.create(None, client=ws_token, callback=handle_msg, private=False)
    orderbook.initialize(symbol)
    # Connect to WebSocket
    await client.subscribe('/market/candles:' + symbol)
    # Enter the application loop
    while True:
        await asyncio.sleep(min(60 - datetime.datetime.now().second, 30))
        # print_market_book(orderbook, ob_depth)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting bot from keyboard interrupt")
        exit(0)
    except ConnectionError:
        print("There was a connection error, resetting...")
        exit(1)
