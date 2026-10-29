# Run every strategy on every ticker, then save the results table and equity curve charts.
# Run from the repo root:  python -m src.results
#
# To add your ticker, append it to TICKERS (it must be a column in data/combined_adj_close.csv).
# New strategy files in src/strategies/ are picked up automatically.

# Imports
import os

import matplotlib
matplotlib.use("Agg")  # save charts to files without opening a window
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd

from src.engine import evaluate, load_risk_free_rate, run_backtest

# Settings
TICKERS = ["QQQ", "AAPL", "AMZN", "TSLA", "JPM", "AMGN", "XOM", "MCD"]
STRATEGY_DIR = "src/strategies"
OUTPUT_DIR = "results"
CHART_DIR = os.path.join(OUTPUT_DIR, "equity_curves")

# Fixed color order so a ticker/strategy keeps the same color on every chart
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]


def find_strategies():
    """Every .py file in src/strategies, with buy_and_hold (the benchmark) first."""
    names = sorted(f[:-3] for f in os.listdir(STRATEGY_DIR)
                   if f.endswith(".py") and not f.startswith("__"))
    if "buy_and_hold" in names:
        names.remove("buy_and_hold")
        names.insert(0, "buy_and_hold")
    return names


def run_all(tickers, strategies):
    """Backtest every ticker/strategy pair.

    Returns the results table (one row per pair) and a dict of equity curves keyed by (ticker, strategy).
    """
    rf = load_risk_free_rate()
    rows = []
    curves = {}
    for ticker in tickers:
        for strategy in strategies:
            print(f"Running {strategy} on {ticker}...")
            result = run_backtest(ticker, strategy)
            curves[(ticker, strategy)] = result["Equity"]
            rows.append({"Ticker": ticker, "Strategy": strategy, **evaluate(result, rf)})
    return pd.DataFrame(rows), curves


def style_axes(ax, title):
    ax.set_title(title, loc="left", fontsize=12)
    ax.set_ylabel(r"Portfolio value (started at \$100)")
    ax.grid(axis="y", color="#e5e5e5", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)


def plot_by_strategy(curves, tickers, strategies):
    """One chart per strategy, one line per ticker."""
    ticker_fmt = matplotlib.ticker.FuncFormatter(lambda y, _: f"{y:,.0f}")
    for strategy in strategies:
        fig, ax = plt.subplots(figsize=(10, 5))
        for i, ticker in enumerate(tickers):
            ax.plot(curves[(ticker, strategy)], label=ticker, color=COLORS[i % len(COLORS)], linewidth=1.5)
        style_axes(ax, f"Equity curve: {strategy}")
        # Log scale so one big winner (e.g. TSLA) doesn't flatten the other lines;
        # equal heights on the chart mean equal % changes
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1, 2, 5)))
        ax.yaxis.set_major_formatter(ticker_fmt)
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylabel(r"Portfolio value (started at \$100, log scale)")
        fig.tight_layout()
        fig.savefig(os.path.join(CHART_DIR, f"{strategy}.png"), dpi=150)
        plt.close(fig)


def plot_by_ticker(curves, tickers, strategies):
    """One chart per ticker, one line per strategy, to compare strategies side by side."""
    for ticker in tickers:
        fig, ax = plt.subplots(figsize=(10, 5))
        for i, strategy in enumerate(strategies):
            ax.plot(curves[(ticker, strategy)], label=strategy, color=COLORS[i % len(COLORS)], linewidth=1.5)
        style_axes(ax, f"{ticker}: all strategies")
        fig.tight_layout()
        fig.savefig(os.path.join(CHART_DIR, f"{ticker}_all_strategies.png"), dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    os.makedirs(CHART_DIR, exist_ok=True)
    strategies = find_strategies()

    table, curves = run_all(TICKERS, strategies)
    table.to_csv(os.path.join(OUTPUT_DIR, "results_table.csv"), index=False)

    plot_by_strategy(curves, TICKERS, strategies)
    plot_by_ticker(curves, TICKERS, strategies)

    # Print the table as a strategy x ticker grid (one block per ticker)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.float_format", "{:.3f}".format)
    print()
    print(table.set_index(["Ticker", "Strategy"]))
    print(f"\nSaved {OUTPUT_DIR}/results_table.csv and charts in {CHART_DIR}/")
