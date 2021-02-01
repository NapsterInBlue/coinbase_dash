import os

import pandas as pd
from coinbase.wallet.client import Client


TRANSACTION_MAP = {"Buy": "add", "Coinbase Earn": "add", "Sell": "subtract"}


def crunch_transaction_hist():
    """
    Read account history from `transactions.csv` to determine your current
    account position
    """
    df = pd.read_csv("transactions.csv", skiprows=range(7))
    df["add_subtract"] = df["Transaction Type"].map(TRANSACTION_MAP)

    df["net_amt"] = df["USD Total (inclusive of fees)"] * (
        df["add_subtract"].map({"add": 1, "subtract": -1})
    )

    gb = df.groupby("Asset")[["net_amt", "Quantity Transacted"]].sum()
    gb.columns = ["account_balance", "total_amount"]

    gb["avg_price_per_coin"] = gb["account_balance"] / gb["total_amount"]

    gb = gb.reset_index()

    return gb


def get_prices_from_acct_bal(acct_bal: pd.DataFrame):
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


def check_for_moves(acct_bal: pd.DataFrame, current_prices: pd.Series):
    """
    Checks how much profit we'd see, after fees, if we sold all of an asset,
    returns the frame, sorted by profit, descending.
    """
    merged = pd.merge(acct_bal, current_prices, left_on="Asset", right_index=True)
    merged["sell_all_profit"] = (
        (merged["current_price_per_coin"] * merged["total_amount"])
        - 1.5
        - merged["account_balance"]
    )

    merged = merged.sort_values("sell_all_profit", ascending=False)
    return merged


if __name__ == "__main__":
    acct_bal = crunch_transaction_hist()
    current_prices = get_prices_from_acct_bal(acct_bal)
    print(check_for_moves(acct_bal, current_prices))
    input()  # stays on the screen until user hits Enter
