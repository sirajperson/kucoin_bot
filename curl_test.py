import base64
import hashlib
import hmac
import json
import time

import requests as requests
import yaml

# with open("configuration.yaml", "r") as file:
#     config = yaml.safe_load(file)
#
# api_key = config["api_key"]
# api_secret = config["api_secret"]
# api_passphrase = config["api_passphrase"]
#
# url = 'https://api.kucoin.com/api/v1/accounts'
# now = int(time.time() * 1000)
#
# str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
# signature = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
# passphrase = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
# headers = {
#     "KC-API-SIGN": signature,
#     "KC-API-TIMESTAMP": str(now),
#     "KC-API-KEY": api_key,
#     "KC-API-PASSPHRASE": api_passphrase,
#     "KC-API-KEY-VERSION": "1"
# }
# response = requests.request('get', url, headers=headers)
# print(response.status_code)
# print(response.json())

from kucoin.client import User
with open("configuration.yaml", "r") as file:
    config = yaml.safe_load(file)

client = User(
            key=config["api_key"],
            secret=config["api_secret"],
            passphrase=config["api_passphrase"],
            is_sandbox=(config["sandbox"] == "True"),
            # is_v1api=True
        )
btc_accounts = client.get_account_list("BTC")
print(btc_accounts)
# # Example for create deposit addresses in python
# url = 'https://api.kucoin.com/api/v1/deposit-addresses'
# now = int(time.time() * 1000)
# data = {"currency": "BTC"}
# data_json = json.dumps(data)
# str_to_sign = str(now) + 'POST' + '/api/v1/deposit-addresses' + data_json
# signature = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
# passphrase = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
# headers = {
#     "KC-API-SIGN": signature,
#     "KC-API-TIMESTAMP": str(now),
#     "KC-API-KEY": api_key,
#     "KC-API-PASSPHRASE": passphrase,
#     # "KC-API-KEY-VERSION": 2,
#     "Content-Type": "application/json"  # specifying content type or using json=data in request
# }
# response = requests.request('post', url, headers=headers, data=data_json)
# print(response.status_code)
# print(response.json())