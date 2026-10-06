import os
import pandas as pd
import yfinance as yf

TICKER = "MCD"
RAW_PATH = f"../data/raw/{TICKER}_raw.csv"
CLEAN_PATH = f"../data/processed/{TICKER}_clean.csv"

os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)

ticker = yf.Ticker(TICKER)

# Unadjusted data, so you can see raw prices vs. adjusted
raw = ticker.history(period="10y", interval="1d", auto_adjust=False)
raw.index = raw.index.tz_localize(None)
raw.to_csv(RAW_PATH)

# Adjusted data (splits + dividends), used for returns
hist = ticker.history(period="10y", interval="1d", auto_adjust=True)
hist.index = hist.index.tz_localize(None)

df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
df.index.name = "Date"

# ---- Checks ----
print("Date range:", df.index.min().date(), "to", df.index.max().date())
print("Rows:", len(df))
print("Missing values:\n", df.isna().sum())
print("Duplicate dates:", df.index.duplicated().sum())
print("Zero-volume days:", (df["Volume"] == 0).sum())

# Gaps longer than 4 days (normal weekends/holidays are up to 4)
gaps = df.index.to_series().diff().dt.days
print("Unusual gaps:\n", gaps[gaps > 4])

# Splits and dividends that were applied
print("Splits:\n", ticker.splits)
print("Dividends (last 5):\n", ticker.dividends.tail())

# Clean: drop NaNs and duplicates, sort by date
df = df.dropna().loc[~df.index.duplicated()].sort_index()

# Daily returns from adjusted close
df["Return"] = df["Close"].pct_change()

df.to_csv(CLEAN_PATH)

import matplotlib.pyplot as plt
df["Close"].plot(title="MCD Adjusted Close")
plt.show()