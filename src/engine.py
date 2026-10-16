# Imports
import importlib
import os

import pandas as pd

# Defaults
DATA_PATH = "data/combined_adj_close.csv"
RF_PATH = "data/DGS3MO.csv"
RF_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3MO"
TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------
def run_backtest(ticker, strategy, capital=100, interest=None, trading_cost=0.0005):
    """Run `strategy` on `ticker` and return a DataFrame with Equity and Shares columns.

    capital       starting cash
    interest      annual interest rate earned on idle cash. Leave as None to use the
                  real 3-month T-bill rate from FRED for each day (same rate the
                  Sharpe ratio uses), or pass a number like 0.02 for a flat rate.
    trading_cost  cost per trade as a fraction of traded value (0.0005 = 5 bps)
    """
    # Load the strategy function dynamically, e.g. src/strategies/buy_and_hold.py
    module = importlib.import_module(f"src.strategies.{strategy}")
    strategy_fn = getattr(module, strategy)

    # Get data for the specified ticker
    df = pd.read_csv(DATA_PATH, index_col="Date", parse_dates=True)
    ticker_data = df[ticker].dropna()

    # Daily interest rate on cash for each trading day
    if interest is None:
        annual = align_rate(load_risk_free_rate(), ticker_data.index)
        # Cash held overnight into day i earns the rate known on day i-1
        daily_rates = ((1 + annual) ** (1 / TRADING_DAYS) - 1).shift(1).fillna(0)
    else:
        flat = (1 + interest) ** (1 / TRADING_DAYS) - 1
        daily_rates = pd.Series(flat, index=ticker_data.index)

    cash = capital
    shares = 0
    equity = pd.DataFrame(index=ticker_data.index, columns=["Equity", "Shares"], dtype=float)

    for i, price in enumerate(ticker_data):
        cash = cash * (1 + daily_rates.iloc[i])  # Apply interest to cash
        cash, new_shares = strategy_fn(cash, shares, ticker_data.iloc[:i + 1])  # Apply the strategy
        if shares != new_shares:
            changed = abs(new_shares - shares)  # Deduct trading cost
            cash -= price * changed * trading_cost
            if cash < 0:
                new_shares -= abs(cash) / price  # Sell shares to cover a negative cash balance
                cash = 0
        equity.iloc[i] = [cash + new_shares * price, new_shares]
        shares = new_shares

    return equity


# ---------------------------------------------------------------------------
# Risk-free rate (FRED)
# ---------------------------------------------------------------------------
def load_risk_free_rate(refresh=False):
    """Return the FRED 3-Month Treasury Bill yield (DGS3MO) as a decimal annual rate.

    The series is downloaded once and cached at data/DGS3MO.csv.
    Pass refresh=True to download a fresh copy.
    """
    if refresh or not os.path.exists(RF_PATH):
        raw = pd.read_csv(RF_URL, na_values=".")
        raw.to_csv(RF_PATH, index=False)

    rf = pd.read_csv(RF_PATH, na_values=".")
    rf.index = pd.to_datetime(rf.iloc[:, 0])  # first column is the date
    return rf["DGS3MO"].astype(float) / 100   # FRED quotes percent, convert to decimal


def align_rate(rf, dates):
    """Line up the FRED rate with our trading days, carrying it forward over FRED holidays."""
    return rf.ffill().reindex(dates, method="ffill").bfill()


# ---------------------------------------------------------------------------
# Performance metrics (each takes the full result DataFrame from run_backtest)
# ---------------------------------------------------------------------------
def daily_returns(result):
    return result["Equity"].pct_change().dropna()


def total_return(result):
    equity = result["Equity"]
    return equity.iloc[-1] / equity.iloc[0] - 1


def annualized_return(result):
    years = (len(result) - 1) / TRADING_DAYS
    return (1 + total_return(result)) ** (1 / years) - 1


def annualized_volatility(result):
    return daily_returns(result).std() * TRADING_DAYS ** 0.5


def sharpe_ratio(result, rf=None):
    """Annualized Sharpe ratio using the daily FRED risk-free rate."""
    if rf is None:
        rf = load_risk_free_rate()
    returns = daily_returns(result)

    rf_annual = align_rate(rf, returns.index)
    rf_daily = (1 + rf_annual) ** (1 / TRADING_DAYS) - 1

    excess = returns - rf_daily
    return excess.mean() / excess.std() * TRADING_DAYS ** 0.5


def max_drawdown(result):
    """Largest peak-to-trough drop, returned as a negative number (-0.35 = -35%)."""
    equity = result["Equity"]
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1
    return drawdown.min()


def win_rate(result):
    """Fraction of days in the market that had a positive return.

    Days sitting fully in cash are skipped, since interest would count them all as wins.
    A day counts as in the market if shares were held going into it (end of the day before).
    """
    returns = daily_returns(result)
    held = result["Shares"].shift(1).reindex(returns.index) > 0
    if not held.any():
        return float("nan")
    return (returns[held] > 0).mean()


def evaluate(result, rf=None):
    """Return every performance metric for one run_backtest result as a dict."""
    return {
        "Total Return": total_return(result),
        "Annualized Return": annualized_return(result),
        "Annualized Volatility": annualized_volatility(result),
        "Sharpe Ratio": sharpe_ratio(result, rf),
        "Max Drawdown": max_drawdown(result),
        "Win Rate": win_rate(result),
    }
