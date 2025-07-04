# Module containing the code for strategies
import pandas as pd
import pandas_ta as ta

def macd_strategy(symbol, master_df, START_DATE, END_DATE):
    df = master_df[symbol].loc[START_DATE:END_DATE]
    close = df['Close']
    ema20 = ta.ema(close, length=20)
    ema50 = ta.ema(close, length=50)

    sig = pd.Series(0, index=close.index)
    cross_up = (ema20 > ema50) & (ema20.shift() <= ema50.shift())
    cross_down = (ema20 < ema50) & (ema20.shift() >= ema50.shift())

    sig.loc[cross_up] = 1
    sig.loc[cross_down] = -1

    return sig, close 


def impulse_macd_rsi_strategy(symbol, master_df, START_DATE, END_DATE):
    df = master_df[symbol].loc[START_DATE:END_DATE]
    close = df['Close']

    # === Indicators ===
    macd = ta.macd(close)
    rsi = ta.rsi(close, length=14)

    # Ensure MACD components are present
    if macd is None or macd.isna().all().any():
        print(f"⚠️ MACD data missing for {symbol}.")
        return pd.Series(0, index=close.index), close

    hist = macd['MACDh_12_26_9']  # MACD histogram

    # === Signal Logic ===
    sig = pd.Series(0, index=close.index)

    # Entry: MACD histogram > 0 and RSI > 50 → Long
    sig[(hist > 0) & (rsi > 50)] = 1

    # Exit / Short: MACD histogram < 0 and RSI < 50 → Short
    sig[(hist < 0) & (rsi < 50)] = -1

    return sig, close


def st_ema_strategy(symbol, master_df, START_DATE, END_DATE):
    df = master_df[symbol].loc[START_DATE:END_DATE]
    close = df['Close']
    high = df['High']
    low = df['Low']

    # === Indicators ===
    supertrend = ta.supertrend(high=high, low=low, close=close, length=10, multiplier=3)
    ema_short = ta.ema(close, length=3)
    ema_long = ta.ema(close, length=20)

    # Make sure required columns exist
    if supertrend is None or supertrend.empty or ema_short is None or ema_long is None:
        return pd.Series(0, index=close.index, dtype=float), close

    # Extract the 'SUPERTd_10_3.0' column for trend direction
    trend_col = [col for col in supertrend.columns if col.startswith('SUPERTd_')]
    if not trend_col:
        return pd.Series(0, index=close.index, dtype=float), close

    trend = supertrend[trend_col[0]]  # +1 for green, -1 for red

    # === Signal Construction ===
    sig = pd.Series(0, index=close.index, dtype=float)

    # Entry condition: Supertrend green (1) and EMA_short > EMA_long
    entry = (trend == 1) & (ema_short > ema_long)
    # Exit condition: Supertrend red (-1) or EMA_long > EMA_short
    exit = (trend == -1) | (ema_long > ema_short)

    sig[entry] = 1
    sig[exit] = -1

    return sig, close


def triple_supertrend_strategy(symbol, master_df, START_DATE, END_DATE):
    df = master_df[symbol].loc[START_DATE:END_DATE].copy()
    close = df['Close']
    high = df['High']
    low = df['Low']

    # Compute multiple Supertrend indicators
    supertrend_1 = df.ta.supertrend(high=high, low=low, close=close, length=10, multiplier=1)["SUPERTd_10_1.0"]
    supertrend_2 = df.ta.supertrend(high=high, low=low, close=close, length=11, multiplier=2)["SUPERTd_11_2.0"]
    supertrend_3 = df.ta.supertrend(high=high, low=low, close=close, length=12, multiplier=3)["SUPERTd_12_3.0"]

    # Initialize signal series
    sig = pd.Series(0, index=close.index)

    # Calculate bullish and bearish agreement (at least 2 out of 3 indicators)
    bullish_agreement = ((supertrend_1 == 1).astype(int) +
                         (supertrend_2 == 1).astype(int) +
                         (supertrend_3 == 1).astype(int)) >= 2

    bearish_agreement = ((supertrend_1 == -1).astype(int) +
                         (supertrend_2 == -1).astype(int) +
                         (supertrend_3 == -1).astype(int)) >= 2

    # Assign signals
    sig[bullish_agreement] = 1
    sig[bearish_agreement] = -1

    return sig, close


def adx_moving_average_strategy(symbol, master_df, START_DATE, END_DATE):
    df = master_df[symbol].loc[START_DATE:END_DATE]
    close = df['Close']
    high = df['High']
    low = df['Low']

    # === Indicators ===
    dmi = ta.adx(high=high, low=low, close=close, length=14)  # DI+, DI−, and ADX
    ema5 = ta.ema(close, length=5)
    sma6 = ta.sma(close, length=6)

    # Check for valid DMI output
    if dmi is None or dmi.empty or ema5 is None or sma6 is None:
        return pd.Series(0, index=close.index, dtype=float), close

    adx = dmi['ADX_14']
    di_plus = dmi['DMP_14']
    di_minus = dmi['DMN_14']

    # === Signal Construction ===
    sig = pd.Series(0, index=close.index, dtype=float)

    # Entry: ADX > 25, DI+ > DI−, EMA5 > SMA6
    entry = (adx > 25) & (di_plus > di_minus) & (ema5 > sma6)

    # Exit: ADX < 35, DI+ < DI−, EMA5 < SMA6
    exit = (adx < 35) & (di_plus < di_minus) & (ema5 < sma6)

    sig[entry] = 1
    sig[exit] = -1

    return sig, close
