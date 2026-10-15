def crossover_50_200(cash,shares,ticker_data):

    current_price = ticker_data.iloc[-1]
    signal_data = ticker_data.iloc[:-1]
    if len(signal_data) < 200:
        return cash, shares


    short_ma = signal_data.iloc[-50:].mean()
    long_ma = signal_data.iloc[-200:].mean()

    if short_ma > long_ma and cash>0:
        shares += cash/current_price
        cash = 0

    elif short_ma < long_ma and shares > 0:
        cash += shares*current_price
        shares = 0

    return cash, shares