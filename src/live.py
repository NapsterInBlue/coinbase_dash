import os
from bisect import bisect

import pandas as pd
from coinbase.wallet.client import Client


def get_prices_from_acct_bal(acct_bal: pd.DataFrame) -> pd.Series:
    """
    Iterate through the "Asset" column and generate simple API calls
    to get the spot price for each asset in USD
    """

    # simple price checks don't require API creds
    client = Client(
        "intentionally_blank", "intentionally_blank", api_version="YYYY-MM-DD"
    )

    price_dict = dict()
    for asset in acct_bal["Asset"]:
        pair = asset + "-USD"
        price_dict[asset] = client.get_spot_price(currency_pair=pair).get("amount")

    current_prices = pd.Series(price_dict, name="current_price_per_coin").astype(float)

    return current_prices


def get_transaction_fee(trade_val: float) -> float:
    """
    Per this write-up

    https://www.gobankingrates.com/investing/crypto/coinbase-fees/
    """

    cutoffs = [10, 25, 50, 200]
    fees = [0.99, 1.49, 1.99, 2.99]

    try:
        index = bisect(cutoffs, trade_val)
        transaction_fee = fees[index]
    except IndexError:
        transaction_fee = 0.00

    return transaction_fee
