import logging
import time

from base_account import BaseAccount
from kucoin.client import User
from exchanges.kucoin.kucoin_exception import KucoinAPIException


class KucoinAccount(BaseAccount):
    def __init__(self, config, get_data_function=None, rest_update_function=None):
        super().__init__(config)
        self._exchange = 'KuCoin'  # Update with your exchange name
        self._account_type = config["account_type"]
        self.log = logging.getLogger("KucoinAccount")
        self.log.setLevel(config["log_level"])
        
        if callable(get_data_function):
            self._get_data = get_data_function

        if callable(get_data_function):
            self._rest_update = rest_update_function

        self._client = User(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"],
            is_sandbox=(config["sandbox"] == "True")
        )

    def get_exchange_fees(self):
        try:
            results = self._client.get_base_fee()
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting base fee: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting base fee: {ex}")
            return None

    def get_account_list(self, currency=None, account_type=None):
        try:
            results = self._client.get_account_list(currency, account_type)
            for account in results:
                cache_object = {
                    "topic": "/account/balance",
                    "accounts": {account_type: {currency: account}}
                }
                self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting account list: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting account list: {ex}")
            return None

    def get_account(self, account_id):
        try:
            results = self._client.get_account(account_id)
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting account: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting account: {ex}")
            return None

    def get_account_ledger(self, currency):
        try:
            kwargs = {
                "currency": currency,
            }
            results = self._client.get_account_ledger(**kwargs)
            self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting account ledger: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting account ledger: {ex}")
            return None

    def get_account_hold(self, account_id):
        try:
            results = self._client.get_account_hold(account_id)
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting account hold: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting account hold: {ex}")
            return None

    def get_sub_account(self, sub_user_id):
        try:
            results = self._client.get_sub_account(sub_user_id)
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting sub account: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting sub account: {ex}")
            return None

    def get_sub_accounts(self):
        try:
            results = self._client.get_sub_accounts()
            # self._rest_update(results)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting sub accounts: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting sub accounts: {ex}")
            return None

    def get_transferable(self, currency, account_type=None):
        try:
            results = self._client.get_transferable(currency, str(account_type).upper())
            cache_object = {
                "topic": "/account/balance",
                "accounts": {account_type: {currency: results}}
            }
            self._rest_update(cache_object)
            return results
        except KucoinAPIException as ex:
            self.log.error(f"API error getting transferable: {ex}")
            return None
        except Exception as ex:
            self.log.error(f"Unexpected error getting transferable: {ex}")
            return None

    def initialize(self):
        self.get_exchange_fees()
        self.get_account_list(self.get_base_symbol(), self._account_type)
        time.sleep(1)
        self.get_account_list(self.get_quote_symbol(), self._account_type)
        self.get_transferable(self.get_base_symbol(), self._account_type)
        self.get_transferable(self.get_quote_symbol(), self._account_type)
        time.sleep(1)

    def ws_get_orders(self):
        data = self._get_data()
        if "orders" in data:
            return data["orders"]
        return None

    def ws_get_order_by_id(self, key, oid):
        data = self._get_data()
        if "orders" in data:
            for order in data["orders"]:
                if order[key] == oid:
                    return order
        return None

    def ws_get_position(self):
        data = self._get_data()
        if "position" in data:
            return data["position"]
        return None
