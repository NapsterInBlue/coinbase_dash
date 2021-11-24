import pandas as pd

from src.live import get_prices_from_acct_bal, get_transaction_fee
from src.parser import crunch_transaction_hist

pd.set_option("display.max_columns", 10)
pd.set_option("display.float_format", "{:,.2f}".format)


def check_for_moves(fpath: str = None) -> pd.DataFrame:
    """
    Checks how much profit we'd see, after fees, if we sold all of each asset.

    Prints a summary table then returns the frame, sorted by profit, desc
    """
    acct_bal = crunch_transaction_hist(fpath)
    current_prices = get_prices_from_acct_bal(acct_bal)

    merged = pd.merge(acct_bal, current_prices, left_on="Asset", right_index=True)

    # revenue
    acct_val_per_coin = merged["current_price_per_coin"] * merged["total_amount_held"]

    # costs, per: https://www.gobankingrates.com/investing/crypto/coinbase-fees/
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
    merged.columns = ["Coin", "Spent", "Amt", "AvgBuy", "CurrPrice", "Fees", "Profit"]

    merged.set_index("Coin", inplace=True)

    return merged


if __name__ == "__main__":
    print(check_for_moves())
