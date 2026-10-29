# Phase 2: statistics for each stock on its own (just holding it, no trading rule).
# Run from the repo root:  python -m src.phase2

# Imports
import os

import pandas as pd

from src.engine import (DATA_PATH, annualized_return, annualized_volatility,
                        load_risk_free_rate, sharpe_ratio)

# Settings
OUTPUT_DIR = "results"


def load_prices():
    """Adjusted close for every ticker, one column each."""
    return pd.read_csv(DATA_PATH, index_col="Date", parse_dates=True).dropna()


def asset_stats(prices, rf=None):
    """Annualized return, annualized volatility and Sharpe ratio for each ticker.

    Uses the same metric functions as the backtests, so the numbers line up with Phase 1.
    Those functions read an "Equity" column, so each price series is passed in as one.
    """
    if rf is None:
        rf = load_risk_free_rate()
    rows = []
    for ticker in prices.columns:
        as_equity = prices[[ticker]].rename(columns={ticker: "Equity"})
        rows.append({
            "Ticker": ticker,
            "Annualized Return": annualized_return(as_equity),
            "Annualized Volatility": annualized_volatility(as_equity),
            "Sharpe Ratio": sharpe_ratio(as_equity, rf),
        })
    return pd.DataFrame(rows).set_index("Ticker").sort_values("Sharpe Ratio", ascending=False)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prices = load_prices()

    stats = asset_stats(prices)
    stats.to_csv(os.path.join(OUTPUT_DIR, "asset_stats.csv"))

    pd.set_option("display.float_format", "{:.3f}".format)
    print(stats)
    print(f"\nSaved {OUTPUT_DIR}/asset_stats.csv")
