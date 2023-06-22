class BaseAsset:
    def __init__(self, config):
        self._base_symbol = config["base_currency"]
        self._quote_symbol = config["quote_currency"]
        self._trade_symbol = self._base_symbol + "-" + self._quote_symbol
        self._market_symbol = self._quote_symbol + "-" + self._base_symbol
        self._candle_length = config["candle_length"]

    def get_base_symbol(self):
        return self._base_symbol

        # Getter for _quote_symbol

    def get_quote_symbol(self):
        return self._quote_symbol

        # Getter for _trade_symbol

    def get_trade_symbol(self):
        return self._trade_symbol

        # Getter for _market_symbol

    def get_market_symbol(self):
        return self._market_symbol

    def get_candle_length(self):
        return self._candle_length
