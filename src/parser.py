from pathlib import Path
import re

import pandas as pd


DEFAULT_CSV_PATH = str(Path(__file__).resolve().parent.parent / "transactions.csv")

TRANSACTION_MAP = {
    "Buy": "add",
    "Coinbase Earn": "add",
    "Convert": "subtract",
    "Receive": "add",
    "Sell": "subtract",
}


def load_data(fpath: str = None) -> pd.DataFrame:
    """
    Loads a csv generated from the "Transaction History" of the "Taxes & Reporting"
    section on Coinbase.
    """
    if not fpath:
        fpath = DEFAULT_CSV_PATH

    return pd.read_csv(fpath, skiprows=range(7))


def make_conversion_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    When you convert one currency to another, it doesn't create a corresponding row
    in the report for the new currency. Instead, the line looks something like
        
        Trans.  Asset   Quan.   Spot    Tot (w fee)  Notes
        --------------------------------------------------
        Convert	MANA	29.98	3.34	100.24  	 Converted 29.98841098 MANA to 36.78628798 LRC

    Per TRANSACTION_MAP, we treat a "Convert" transaction as a "subtract" for tabulation, but we
    still need to add equivalent "add" rows for the currency that we converted to.
    """
    conversions = df[df['Transaction Type'] == 'Convert']

    rows = []

    for idx, row in conversions.iterrows():
        spent = row['Subtotal']
        notes = row['Notes']

        _, _, amt, asset = re.findall('([\d\.]+) ([A-Z]+) to ([\d\.]+) ([A-Z\d]+)', notes)[0]

        rows.append(pd.Series({
            'Transaction Type': 'Buy',
            'Asset': asset,
            'Quantity Transacted': float(amt),
            'Spot Price at Transaction': spent / float(amt),
            'Total (inclusive of fees)': spent,
            'add_subtract': 'add',}))

    return pd.DataFrame(rows)

def crunch_transaction_hist(fpath: str = None) -> pd.DataFrame:
    """
    Loads the data from the given fpath, then

        - Adds offsetting Convert rows, where necessary
        - Encodes $ amt and quantity, based on whether the line item
          was an addition or subtraction
        - Aggregates each asset by its name

    Returns a DataFrame with columns:
        - Asset
        - Total Spent
        - Number of coins held
        - Avg price per coin
    """
    df = load_data(fpath)

    df["add_subtract"] = df["Transaction Type"].map(TRANSACTION_MAP)
    if df["add_subtract"].isnull().sum() != 0:
        raise RuntimeError("Unknown value in `Transaction Type` column")

    conversions = make_conversion_rows(df)
    df = df.append(conversions)

    df["net_amt"] = df["Total (inclusive of fees)"] * (
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
