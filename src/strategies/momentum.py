LOOKBACK = 252   # ~12 months of trading days
SKIP = 21        # skip the most recent month (short-term reversal)
REBALANCE = 21   # check the signal about once a month to limit trading costs


def momentum(cash, shares, ticker_data):
    n = len(ticker_data)

    # Not enough history yet, or not a rebalance day: do nothing
    if n <= LOOKBACK or n % REBALANCE != 0:
        return cash, shares

    price = ticker_data.iloc[-1]
    past_return = ticker_data.iloc[-1 - SKIP] / ticker_data.iloc[-1 - LOOKBACK] - 1

    if past_return > 0:
        # Past 12-month winner: spend all the cash on shares
        shares += cash / price
        cash = 0
    else:
        # Loser: sell everything
        cash += shares * price
        shares = 0

    return cash, shares
