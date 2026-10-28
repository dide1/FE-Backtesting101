def rsi_mean_reversion(cash,shares,ticker_data):


    current_price = ticker_data.iloc[-1]
    signal_data = ticker_data.iloc[:-1]

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
    #oversold: spend all the cash on shares
    if rsi < 30 and cash > 0:
        shares += cash/current_price
        cash = 0
    #reverted back above neutral: sell everything
    elif rsi > 50 and shares > 0:
        cash += shares * current_price
        shares = 0

    return cash, shares
