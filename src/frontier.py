# Phase 2, step 3: simulate random portfolios and trace the Markowitz efficient frontier.
# Run from the repo root:  python -m src.frontier

# Imports
import os

import matplotlib
matplotlib.use("Agg")  # save the chart to a file without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.engine import TRADING_DAYS

# Settings
PRICE_PATH = "data/combined_adj_close.csv"
OUTPUT_PATH = os.path.join("results", "efficient_frontier.png")
NUM_PORTFOLIOS = 5000
NUM_FRONTIER_POINTS = 50
SEED = 42


def load_stats():
    """Annualized expected return (per asset) and covariance matrix from daily adjusted closes."""
    prices = pd.read_csv(PRICE_PATH, index_col=0, parse_dates=True)
    daily = prices.pct_change().dropna()
    return daily.mean() * TRADING_DAYS, daily.cov() * TRADING_DAYS


def portfolio_stats(weights, mu, cov):
    """Return (annual return, annual volatility) for a vector of weights."""
    ret = weights @ mu
    vol = np.sqrt(weights @ cov @ weights)
    return ret, vol


def random_portfolios(mu, cov, n=NUM_PORTFOLIOS, seed=SEED):
    """Random long-only portfolios: non-negative weights that sum to 1."""
    rng = np.random.default_rng(seed)
    weights = rng.dirichlet(np.ones(len(mu)), size=n)  # each row sums to 1
    rets = weights @ mu.values
    vols = np.sqrt(np.einsum("ij,jk,ik->i", weights, cov.values, weights))
    return rets, vols


def minimize_volatility(mu, cov, target_return=None):
    """Lowest-volatility long-only portfolio, optionally forced to hit a target return."""
    n = len(mu)
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    if target_return is not None:
        constraints.append({"type": "eq", "fun": lambda w: w @ mu.values - target_return})
    result = minimize(
        lambda w: np.sqrt(w @ cov.values @ w),
        x0=np.ones(n) / n,
        bounds=[(0, 1)] * n,
        constraints=constraints,
        method="SLSQP",
    )
    return result.x


def efficient_frontier(mu, cov, n_points=NUM_FRONTIER_POINTS):
    """Trace the frontier: for each target return, find the least risky portfolio."""
    min_var_return = minimize_volatility(mu, cov) @ mu.values
    targets = np.linspace(min_var_return, mu.max(), n_points)
    vols = [portfolio_stats(minimize_volatility(mu, cov, t), mu.values, cov.values)[1] for t in targets]
    return targets, np.array(vols)


def plot(rand_rets, rand_vols, front_rets, front_vols, mu, cov):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(rand_vols, rand_rets, s=6, alpha=0.4, color="#2a78d6", label=f"{len(rand_rets):,} random portfolios")
    ax.plot(front_vols, front_rets, color="#e34948", linewidth=2.5, label="Efficient frontier")

    # Each single stock on its own, for reference
    asset_vols = np.sqrt(np.diag(cov.values))
    ax.scatter(asset_vols, mu.values, color="black", s=30, zorder=3)
    for name, x, y in zip(mu.index, asset_vols, mu.values):
        ax.annotate(name, (x, y), textcoords="offset points", xytext=(5, 4), fontsize=9)

    ax.set_xlabel("Annualized volatility (risk)")
    ax.set_ylabel("Annualized return")
    ax.set_title("Random portfolios and the Markowitz efficient frontier")
    ax.legend()
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    mu, cov = load_stats()
    rand_rets, rand_vols = random_portfolios(mu, cov)
    front_rets, front_vols = efficient_frontier(mu, cov)
    plot(rand_rets, rand_vols, front_rets, front_vols, mu, cov)

    print(f"Saved {OUTPUT_PATH}")
    print(f"Random portfolios: volatility {rand_vols.min():.1%} to {rand_vols.max():.1%}, "
          f"return {rand_rets.min():.1%} to {rand_rets.max():.1%}")
    print(f"Frontier: volatility {front_vols.min():.1%} to {front_vols.max():.1%}, "
          f"return {front_rets.min():.1%} to {front_rets.max():.1%}")
