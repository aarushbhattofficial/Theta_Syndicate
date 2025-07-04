# 1. Setup and Imports
import pandas as pd
import numpy as np
np.NaN=np.nan# to resolve error in importing pandas_ta
import pandas_ta as ta
import os
import strategy

# 2. Load consolidated OHLC data based on timeframe
BASE_DIR = 'data/niftysmallcap100'
TIMEFRAME='D'
df_paths = {
    'D': os.path.join(BASE_DIR, 'niftysmallcap100_daily_ohlcv.csv'),
    'W': os.path.join(BASE_DIR, 'niftysmallcap100_weekly_ohlcv.csv'),
    'M': os.path.join(BASE_DIR, 'niftysmallcap100_monthly_ohlcv.csv')
}

if TIMEFRAME not in df_paths:
    raise ValueError(f"Unsupported TIMEFRAME: {TIMEFRAME}. Available: {list(df_paths.keys())}")

file_path = df_paths[TIMEFRAME]
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Data file not found at {file_path}. Please check BASE_DIR and filenames.")

master_df = pd.read_csv(
    file_path,
    header=[0, 1],
    parse_dates=[0],
    index_col=0
)
master_df.columns.names = ['Ticker', 'Field']

SYMBOLS = master_df.columns.get_level_values('Ticker').unique().tolist()
START_DATE = master_df.index.min().strftime('%Y-%m-%d')
END_DATE = master_df.index.max().strftime('%Y-%m-%d')

# 3. Build Portfolio Signals DataFrame with Limits
dates = pd.date_range(start=START_DATE, end=END_DATE, freq=TIMEFRAME)
all_signals = pd.DataFrame(0, index=dates, columns=SYMBOLS)#final dataframe to output
raw_signals = {}#raw dataframe to be processed
raw_prices = {}

for sym in SYMBOLS:
    # IMPORT A DIFFERENT FUNCTION IN THE NEXT LINE TO CHANGE THE STRATEGY USED
    sig, price = strategy.adx_moving_average_strategy(sym, master_df, START_DATE, END_DATE) # strategy function imported from the module
    raw_signals[sym] = sig.reindex(dates, fill_value=0)
    raw_prices[sym] = price.reindex(dates).ffill()
raw_signals = pd.DataFrame(raw_signals)# these signals are only created based on strategy and are not till now limited.
raw_prices = pd.DataFrame(raw_prices)

raw_signals.to_csv('auxilary/trading_signals.csv')
print("Saved trading_signals.csv with shape", raw_signals.shape)

