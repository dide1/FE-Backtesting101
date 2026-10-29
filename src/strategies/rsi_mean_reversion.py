
def rsi_mean_reversion(cash,shares,ticker_data):


    current_price = ticker_data.iloc[-1]
    signal_data = ticker_data.iloc[:-1]
    #do nothing if there is less than 15 days of data
    if(len(signal_data) < 15):
        return cash, shares
    #creates df of changes
    changes = signal_data.diff()
    # separate change data into gains and losses
    gains = changes.clip(lower=0)
    losses = -changes.clip(upper=0)
    # find 14 day average gain and loss
    average_gain = gains.iloc[-14:].mean()
    average_loss = losses.iloc[-14:].mean()

    #calculate RSI
    if average_gain == 0 and average_loss == 0:
        rsi = 50
    elif average_loss == 0:
        rsi = 100
    else:
        rs = average_gain/average_loss
        rsi = 100 - (100/(1+rs))
    #buys a ratio of your cash in stock depending on RSI when above threshold
    if rsi < 30 and cash > 0:
        buy_ratio = (30 - rsi) / 30

        spending = cash * buy_ratio
        shares += spending/current_price
        cash -= spending
    #sells a ratio of your stock depending on RSI when below threshold
    elif rsi > 50 and shares > 0:
        sell_ratio = (rsi -50) /50

        selling = shares * sell_ratio
        cash += selling * current_price
        shares -= selling

    return cash, shares