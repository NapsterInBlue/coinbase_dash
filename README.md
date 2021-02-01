## Coinbase Dash

Quick utility for checking how much money I lose being a crypto whale.


### Overview

I wrote this because I was tired of not being able to see how much I was up/down at a glance.

The script aggregates your transaction history to give you a per-asset balance, then calls out to the Coinbase API to get the current spot price for each asset. Finally, it goes through each row and tells you how much you'd gain (after fees) if you sold off the whole holding.

![img](docs/example.PNG)

*Picked these mostly at random. I am not a financial advisor, lol*

Simple UI element in Robinhood, an hour of scripting around the biggest crypto exchange.... but this is somehow the future?

### Setup and Use

Installation is straight-forward.

1. Install Python (I used 3.8)
2. Clone this repository somewhere on your machine.
3. Navigate to the directory and ensure you have all the requisite libraries using

```
pip install -r requirements.txt
```

Actually using it is as easy as

1. Log into Coinbase and go to `User -> Taxes & Reports`
2. On the right, you should see a button titled `Generate Report`. Click that and save as `.csv`
3. Rename this file to `transactions.csv` and move it to the directory you created above
4. Run everything by opening a terminal, navigating to the directory, and running

```
python checker.py
```

### Misc

[The site has a pretty robust API](https://developers.coinbase.com/) which I'm sure could lead to some really promising tool development. However, but I really don't think Crypto is for me.

* The volatility is far greater than I care to keep up with
* The flat transaction fee strongly disincentivizes small-quantity trading, which is all I really have an appetite for

Regardless, I hope this proves useful to anyone with more patience for this stuff than me!