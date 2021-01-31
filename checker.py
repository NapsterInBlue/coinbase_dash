import os

from coinbase.wallet.client import Client


cb_key = os.environ["CB_KEY"]
cb_secret = os.environ["CB_SECRET"]

client = Client(cb_key, cb_secret, api_version="YYYY-MM-DD")

transactions = client.get_current_user()

print(transactions)

print("this hit")

# for crypto in ["BAND", "BAT", "BTC"]:
#     pair = crypto + "-USD"
#     print(client.get_spot_price(currency_pair=pair))
#     client.get_report