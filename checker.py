import os
from bisect import bisect

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
    df["Quantity Transacted"] = df["Quantity Transacted"] * (
        df["add_subtract"].map({"add": 1, "subtract": -1})
    )

    gb = df.groupby("Asset")[["net_amt", "Quantity Transacted"]].sum()
    gb.columns = ["total_amount_spent", "total_amount_held"]

    gb["avg_price_per_coin_bought"] = gb["total_amount_spent"] / gb["total_amount_held"]

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


def get_transaction_fee(trade_val: float):

    cutoffs = [10, 25, 50, 200]
    fees = [0.99, 1.49, 1.99, 2.99]

    try:
        index = bisect(cutoffs, trade_val)
        transaction_fee = fees[index]
    except IndexError:
        transaction_fee = 0.00

    return transaction_fee


def check_for_moves(acct_bal: pd.DataFrame, current_prices: pd.Series):
    """
    Checks how much profit we'd see, after fees, if we sold all of an asset,
    returns the frame, sorted by profit, descending.
    """
    merged = pd.merge(acct_bal, current_prices, left_on="Asset", right_index=True)

    # revenue
    acct_val_per_coin = merged["current_price_per_coin"] * merged["total_amount_held"]

    # costs
    spread_fee = acct_val_per_coin * 0.005

    conversion_fee = acct_val_per_coin * 0.0149
    transaction_fee = acct_val_per_coin.map(get_transaction_fee)
    max_c_or_t_fee = conversion_fee.combine(transaction_fee, max)

    total_fees_for_coin = spread_fee + max_c_or_t_fee
    merged["total_fees_for_coin"] = total_fees_for_coin

    # profit
    profit = acct_val_per_coin - total_fees_for_coin - merged["total_amount_spent"]
    merged["sell_all_profit"] = profit

    # top-level stats
    current_account_value = acct_val_per_coin.sum()
    total_spent = merged["total_amount_spent"].sum()
    total_fees = total_fees_for_coin.sum()
    total_profit = profit.sum()
    roi = (total_spent + total_profit) / total_spent

    for val, string in [
        (current_account_value, "Account Value"),
        (total_spent, "Total spent"),
        (total_fees, "Total fees"),
        (total_profit, "Profit if Cash Out"),
        (roi, "ROI"),
    ]:
        fmtd_val = f"{val:.2f}".rjust(10)
        print(fmtd_val, " : ", string)
    else:
        print()

    merged = merged.sort_values("sell_all_profit", ascending=False)
    return merged


if __name__ == "__main__":
    acct_bal = crunch_transaction_hist()
    current_prices = get_prices_from_acct_bal(acct_bal)
    df = check_for_moves(acct_bal, current_prices)
    df.columns = ["Coin", "Spent", "Amt", "AvgBuy", "CurrPrice", "Fees", "Profit"]
    print(df)
    input()  # stays on the screen until user hits Enter
