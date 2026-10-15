# Imports
import pandas as pd
import importlib

# Constants
INITIAL_CAPITAL = 100
TICKER = "AAPL"
STRATEGY = "buy_and_hold"
INTEREST_RATE = 0.02
TRADING_COST = 0.0005
DAILY_RATE = (1 + INTEREST_RATE) ** (1 / 252) - 1

# Load the strategy function dynamically
module = importlib.import_module(f"src.strategies.{STRATEGY}")  # loads src/strategies/buy_and_hold.py
strategy_fn = getattr(module, STRATEGY)                          # grabs the buy_and_hold function inside it

# Get data for the specified ticker
df = pd.read_csv("data/combined_adj_close.csv", index_col="date", parse_dates=True)
ticker_data = df[TICKER]

# ENGINE:
cash = INITIAL_CAPITAL
shares = 0
equity = pd.DataFrame(index=ticker_data.index, columns=["Equity", "Shares"], dtype=float)

for i, price in enumerate(ticker_data):
    cash = cash * (1 + DAILY_RATE)  # Apply interest to cash
    cash, new_shares = strategy_fn(cash, shares, ticker_data.iloc[:i+1])  # Apply the strategy
    if shares != new_shares:
        changed = abs(new_shares - shares) # Deduct trading cost
        cash -= (price * changed * TRADING_COST)
        if cash < 0:
            new_shares -= (abs(cash) / price)  # Adjust shares if cash goes negative
            cash = 0
    equity.iloc[i] = [cash + (new_shares * price), shares]
    shares = new_shares



