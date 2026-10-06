import pandas as pd
import yfinance as yf


TICKERS = ["AAPL", "AMGN"]

START_DATE = "2016-10-06"
END_DATE = "2026-10-06"


for ticker_name in TICKERS:

    FILE_PATH = f"data/{ticker_name}_clean.csv"

    ticker = yf.Ticker(ticker_name)

    df = ticker.history(
        start=START_DATE,
        end=END_DATE,
        interval="1d",
        auto_adjust=False,
        actions=True
    )

    #Remove timezone from dates
    df.index = df.index.tz_localize(None)
    df.index.name = "Date"

    #Checks

    print(f"\n--- {ticker_name} ---")

    print(
        "Date range:",
        df.index.min().date(),
        "to",
        df.index.max().date()
    )

    print("Rows:", len(df))

    print("\nMissing values:")
    print(df.isna().sum())

    print(
        "\nDuplicate dates:",
        df.index.duplicated().sum()
    )

    #Check unusual gaps
    gaps = df.index.to_series().diff().dt.days
    print("\nUnusual gaps:")
    print(gaps[gaps > 4])

    #Show splits in sample period
    splits = df[df["Stock Splits"] != 0]["Stock Splits"]

    print("\nSplits:")
    if splits.empty:
        print("None")
    else:
        print(splits)

    #Show dividends in sample period
    dividends = df[df["Dividends"] != 0]["Dividends"]

    print("\nDividends:")
    if dividends.empty:
        print("None")
    else:
        print(dividends)

    #Cleaning

    df = (
        df
        .dropna()
        .loc[~df.index.duplicated()]
        .sort_index()
    )

    # Returns must use adjusted close
    df["Return"] = df["Adj Close"].pct_change()

    df.to_csv(FILE_PATH)

    print(f"\nSaved {ticker_name} to {FILE_PATH}")