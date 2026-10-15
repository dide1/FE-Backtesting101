def buy_and_hold(cash, shares, ticker_data):
    # Spend all the cash to buy shares at the current price
    price = ticker_data.iloc[-1]
    if cash != 0:
        shares += cash / price
        cash = 0

    return cash, shares