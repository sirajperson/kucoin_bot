from base_asset import BaseAsset


class BaseMarket(BaseAsset):
    def __init__(self, config):
        super().__init__(config)
        self._market_type = config["account_type"]

    def get_market_type(self):
        return self._market_type
