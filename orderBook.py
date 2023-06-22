import asyncio
import datetime
import pandas as pd
import yaml
from kucoin.client import Market, WsToken
from kucoin.ws_client import KucoinWsClient

# Fetch Initial Orderbook Data
with open("configuration.yaml", "r") as file:
    config = yaml.safe_load(file)

# Get WebSocket token
ws_token = WsToken(
    key=config["api_key"],
    secret=config["api_secret"],
    passphrase=config["api_passphrase"]
)

class KLines:
    def __init__(self):
        self.orderbook = None
        self.market = Market(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"])
        self.klines = None

    def initialize(self, symbol):
        self.klines = []
        raw_klines = self.market.get_kline(symbol, "1min")
        # Convert the data types
        for kline in raw_klines:
            self.klines.append([int(kline[0])] + [float(x) for x in kline[1:]])

    def update_klines(self, message):
        raw_update_candle = message["data"]["candles"]
        # Explicitly convert the first value to int and the rest to float
        update_candle = [int(raw_update_candle[0])] + [float(x) for x in raw_update_candle[1:]]

        if not self.klines or update_candle[0] > self.klines[0][0]:
            # This is a new minute, insert the new candle at the top
            self.klines.insert(0, update_candle)
            # Remove the last element if the length exceeds 100
            if len(self.klines) > 100:
                self.klines.pop()
        else:
            # This is the same minute, update the 0th element
            self.klines[0] = update_candle

    def print_klines(self, n_records):
        series_headers = ["open_time", "open", "close", "high", "low", "volume", "amount"]
        df = pd.DataFrame(self.klines, columns=series_headers).head(n_records)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
        print(df.to_markdown())


klines = KLines()


def create_handle_msg(update_ob):
    async def handle_msg(msg):
        # Process the WebSocket message
        # print(msg)  # Add this line to print the message
        topic = msg['topic']
        if 'candles' in topic:
            update_ob.update_klines(msg)

    return handle_msg


async def main():
    symbol = 'BTC-USDT'

    # Create the handle_msg function with access to orderbook
    handle_msg = create_handle_msg(klines)
    # Connect to WebSocket
    client = await KucoinWsClient.create(None, client=ws_token, callback=handle_msg, private=False)
    # orderbook.initialize(symbol)
    klines.initialize(symbol)
    await client.subscribe('/market/candles:' + symbol + "_" + '1min')
    # Enter the application loop
    while True:
        klines.print_klines(20)
        await asyncio.sleep(min(60 - datetime.datetime.now().second, 30))


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
