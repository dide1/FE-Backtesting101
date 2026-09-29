# From Signals to Smart Portfolios: Backtesting 101

**Level:** Freshman / Underclassmen

## Overview

This project combines two introductory building blocks for many quant projects, strategy backtesting and portfolio diversification, into one full research project that mirrors how a real quantitative portfolio manager works: first find and test candidate trading signals ("alpha"), and then figure out how to combine them into a portfolio that manages risk intelligently.

The central question of the semester: **does diversifying across trading strategies add value beyond simply diversifying across raw assets?**

## Stock Universe

| Ticker | Name | Type / Sector | Data Cleaning Owner |
|---|---|---|---|
| QQQ | Invesco QQQ Trust | Index ETF (Nasdaq-100) | Nathan |
| AAPL | Apple | Technology | Manoj |
| AMZN | Amazon | Consumer Discretionary / Technology | Nikhil |
| TSLA | Tesla | Automotive / Consumer Discretionary | Fiona |
| JPM | JPMorgan Chase | Financials | Charles |
| LLY | Eli Lilly | Pharmaceuticals | Unassigned |
| AMGN | Amgen | Biotechnology | Manoj |
| XOM | ExxonMobil | Energy | Neel |
| MCD | McDonald's | Consumer Staples / Restaurants | Vivek |

Sample period: at least 8-10 years of daily data so results span more than one market regime.

## Setup

Requires Python 3.12+.

```powershell
# Create and activate the virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

On macOS / Linux, activate with `source .venv/bin/activate` instead.

Dependencies: `pandas`, `yfinance`, `matplotlib`, `scipy`.

## Project Phases

### Phase 1: Backtesting Strategies

1. **Setup environment:** Install Python and work through a short pandas/matplotlib tutorial. Set up a shared GitHub repo for the team.
2. **Pick a stock universe:** 6-10 tickers spanning index ETFs and individual stocks across different sectors (see table above). Sample period of at least 8-10 years.
3. **Download and clean data:** Use `yfinance` to pull daily OHLCV data. Check for missing days, stock splits, and dividend adjustments (use adjusted close for return calculations). Keep the cleaned dataset well organized.
4. **Implement a Buy-and-Hold benchmark.**
5. **Implement at least three strategies:**
   - Moving-average crossover (e.g., the 50/200-day "Golden Cross")
   - Momentum (buy the past 12-month winners)
   - Mean reversion (e.g., buy when 14-day RSI falls below 30)
6. **Backtest each rule on each ticker:** Generate daily positions from each signal, apply them to next-day returns to avoid look-ahead bias, and build equity curves.
7. **Evaluate performance:** For every strategy/ticker combination, compute total and annualized return, annualized volatility, Sharpe ratio, maximum drawdown, and win rate.

### Phase 2: Diversification and the Efficient Frontier

1. **Compute individual asset statistics:** Reusing the Phase 1 price data, calculate annualized return, annualized volatility, and Sharpe ratio for each raw asset (buy-and-hold).
2. **Build the correlation matrix:** Compute and visualize (heatmap) the correlation matrix across all assets. Identify the most and least correlated pairs and discuss why.
3. **Simulate random portfolios and trace the efficient frontier:** Generate several thousand random-weight portfolios, plot them on a risk-return scatter, and use `scipy.optimize` to trace the Markowitz efficient frontier on top of that cloud.
4. **Identify and interpret key portfolios:** Label the minimum-variance and maximum-Sharpe ("tangency") portfolios and compare them to an equal-weighted portfolio and to holding a single index ETF alone.

### Phase 3: Build a Diversified Multi-Strategy Portfolio

1. **Build a strategy return matrix:** Treat each strategy/ticker return series from Phase 1 as its own "asset." Assemble these into a single returns matrix (strategies as columns, time as rows).
2. **Compute the strategy correlation matrix:** Are the strategies diversifying against each other, or do they all win and lose at the same time? Visualize as a heatmap and compare to the raw-asset correlation matrix from Phase 2.
3. **Trace an efficient frontier of strategies:** Repeat the Phase 2 approach, but with strategies (or strategy/ticker pairs) as the assets being combined.
4. **Compare three portfolios head-to-head:**
   - (a) the single best individual strategy from Phase 1
   - (b) the diversified raw-asset portfolio from Phase 2
   - (c) the diversified multi-strategy portfolio from this phase
5. **Answer the central question:** Does diversifying across trading strategies add value beyond diversifying across raw assets? Under what conditions would you expect that to be true or false?

## Data Sources

- **Yahoo Finance** via the `yfinance` package: daily OHLCV data, dividends, and splits. The primary data source for all three phases.
- **FRED** (Federal Reserve Economic Data, https://fred.stlouisfed.org): risk-free rate series for computing Sharpe ratios precisely.

## Stretch Goals (Optional)

- Add a simple transaction-cost model (e.g., 5-10 bps per trade) in Phase 1 and see how much it changes which strategies look attractive by Phase 3.
- Test parameter sensitivity (e.g., 20/50 vs. 50/200-day moving averages) as a first taste of overfitting risk.
- Add a risk-free asset and draw the Capital Market Line on both the Phase 2 and Phase 3 frontiers.
- Backtest the Phase 3 multi-strategy weights out-of-sample (fit on an earlier period, evaluate on a later, unseen period).
- Compare performance across two distinct sub-periods (e.g., pre- and post-2020) at each phase to test how stable conclusions are across market regimes.

## Expected Outcomes

- **Final report** (8-10 pages) covering methodology and results for all three phases and a clearly stated answer to the Phase 3 integration question.
- **Poster** summarizing the main methodology and results for the project showcase.

## References & Further Reading

- Investopedia: "Sharpe Ratio," "Maximum Drawdown," "Golden Cross," "Relative Strength Index (RSI)," "Modern Portfolio Theory," "Efficient Frontier," "Correlation Coefficient."
- Markowitz, H., 1952, "Portfolio Selection," *The Journal of Finance*, Vol. 7, No. 1, 77-91.
- Chan, E., *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*, Wiley.
- Bodie, Z., A. Kane, and A. Marcus, *Investments*, any edition.
- [yfinance documentation](https://pypi.org/project/yfinance/)
- [scipy.optimize documentation](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [QuantConnect Boot Camp](https://www.quantconnect.com/learning) lessons on backtesting fundamentals.
