import asyncio
import datetime
import math
import time
import yaml
from check_config import Check as check
from exchanges.kucoin.kucoin_exchange import KucoinExchange
from mailer import Mailer
from trading_strategy import TradingStrategy
import logging


def _check_config_file(config):
    check().config_file(
        {
            "api_key": "No 'api_key' variable in the configuration file.",
            "api_secret": "No 'api_secret' variable in the configuration file.",
            "receiver_email": "No receiver_email variable in the configuration file.",
            "sender_email": "No 'sender_email' variable in the configuration file.",
            "server": "No 'server' variable in the configuration file.",
            "port": "No 'port' variable in the configuration file.",
        }, config)


class KucoinBot:
    _MAX_ERR = 60

    def __init__(self):
        self._init_bot()

    def _init_bot(self):
        try:
            with open("configuration.yaml", "r") as file:
                config = yaml.safe_load(file)
                _check_config_file(config)

                self.log = logging.getLogger("KucoinBot")
                self.log.setLevel(config["log_level"])

                self._exchange = KucoinExchange(config)
                self._strategy = TradingStrategy(config, self._exchange)
                self._mailer = Mailer(config)
                self.run_application = True

        except FileNotFoundError as fnf:
            self.log.error(
                "Cannot run bot. The configuration.yaml file was not "
                "found. Please provide a valid configuration file.",
                fnf)
            SystemExit(1)

    async def connect_websocket(self):
        self.log.info("Connecting web socket client...")
        self._init_bot()
        async def con_ws():
            conn_err = 0
            while not self._exchange.ws_is_connected():
                try:
                    ws_client = await self._exchange.connect_websocket_client()
                    self.log.info("Client connected... ")
                    print("Client connected...")
                    return ws_client
                except Exception as ex:
                    self.log.error(f"Could not connect.\n{ex}\nSleeping for 5 seconds...")
                    print(f"Could not connect.\n{ex}\nSleeping for 5 seconds...")
                    conn_err += 1
                    await asyncio.sleep(5)
                    if conn_err > self._MAX_ERR:
                        self._exit_error()
                    self.log.info("Trying to connect...")

        async def init_data():
            error_count = 0
            data_initialized = False
            while not data_initialized:
                try:
                    self._strategy.initialize()
                    data_initialized = True
                except Exception as ex:
                    self.log.error(ex)
                    error_count += 1
                    if error_count > self._MAX_ERR:
                        self._exit_error()
                    # Try to initialize again.
                    await asyncio.sleep(60 - datetime.datetime.now().second)

        await asyncio.gather(
            con_ws(),
            init_data()
        )

    def _exit_error(self, ex=Exception):
        dt = datetime.datetime.now()
        message = f"{dt} ERROR\nThe application has encountered an error, and could not initialize.\n" \
                  f"The service has terminated for the remainder of this day..\n"
        logging.error(message, ex)
        self._mailer.send_error_message(
            message + "Please review the logs\n"
        )
        time.sleep(60 - datetime.datetime.now().second)
        time.sleep((60 - datetime.datetime.now().minute) * 60)
        self._mailer.send_error_message(
            message + "Please review the logs\n"
        )
        # Sleep till the end of the day
        time.sleep(24 - datetime.datetime.now().hour * math.pow(60, 2))
        SystemExit(1)

    async def run(self):
        try:
            await self.connect_websocket()
            # Main loop for the bot, handling data updates and order management
            # enter the application loop
            while self.run_application:
                try:
                    self._strategy.update_market_data()
                    self._strategy.print_market_data()
                    # Sleep until the start of the next minute
                    now = datetime.datetime.now()
                    sleep_seconds = 60 - now.second - now.microsecond / 1000000
                    await asyncio.sleep(sleep_seconds + 1)

                    self._exchange.market().get_aggregated_orderv3()

                except ConnectionError:
                    print("There was a connection error, resetting...")
                    self._exchange.uninitialize_ws()
                    # Re-connect to the WebSocket
                    await self.connect_websocket()

        except Exception as ex:
            print(ex)

    async def close_websocket(self):
        await self._exchange.unsubscribe()


if __name__ == "__main__":
    bot = KucoinBot()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        print("Exiting bot from keyboard interrupt")
        loop.run_until_complete(bot.close_websocket())
        loop.close()
        exit(0)
    except ConnectionError:
        print("There was an connection error, resetting...")
        loop.run_until_complete(bot.close_websocket())
        loop.close()
        exit(1)
