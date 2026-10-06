import yfinance as yf

TICKER = "XOM"
FILE_PATH = "../data/processed/XOM_close.csv"

ticker = yf.Ticker(TICKER)
hist = ticker.history(period="10y", interval="1d")
close = hist['Close']
close.to_csv(FILE_PATH)