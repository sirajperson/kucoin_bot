from datetime import timezone

from base_asset import BaseAsset
import logging
import pandas as pd
import pandas_ta as ta

class KCTa(BaseAsset):
    def __init__(self, config=None, get_data_function=None):
        super().__init__(config)

        if config is None:
            SystemExit(1)
        self.log = logging.getLogger("KCTa")
        self.log.setLevel(config["log_level"])
        self._candle_delta = config["candle_length"]
        self._sma_period = config["sma_period"]
        self._exchange = f"Kucoin {self.get_trade_symbol()} {self._sma_period} {self._candle_delta}"
        if callable(get_data_function):
            self._get_data = get_data_function

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

    def get_period(self):
        return self._sma_period

    def get_delta(self):
        return self._candle_delta

    def get_ta(self) -> pd.DataFrame:
        series_headers = ["open_time", "open", "close", "high", "low", "volume", "amount"]
        df = pd.DataFrame(self._get_data()['klines'], columns=series_headers)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
        df['open_time'] = df['open_time'].dt.tz_localize('UTC').dt.tz_convert(
            'America/New_York')  # replace 'America/New_York' with your timezone
        return df[::-1]

    def get_bbands(self, leng=20, st_dev=2, oclh=None):
        if oclh is None:
            return self.get_ta().ta.bbands(close='close', length=leng, std=st_dev, append=True)
        else:
            return oclh.ta.bbands(close="close", length=leng, std=st_dev, append=True)
