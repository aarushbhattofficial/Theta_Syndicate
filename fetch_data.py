import pandas as pd
import yfinance as yf
from datetime import datetime

START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')
INTERVALS = {
    '1d': 'data/nifty500_daily_ohlcv.csv',
    '1wk': 'data/nifty500_weekly_ohlcv.csv',
    '1mo': 'data/nifty500_monthly_ohlcv.csv'
}


df = pd.read_csv(r'data/ind_nifty500list.csv')
tickers = [f"{symbol}.NS" for symbol in df['Symbol']]

for interval in INTERVALS:
    # 2. Download daily OHLCV data
    data = yf.download(
        tickers=tickers,
        start=START_DATE,       
        end=END_DATE,
        interval=interval,   # Daily interval
        group_by='ticker',   # Organize data by ticker
        auto_adjust=False,   # Keep original OHLC values
        threads=True         # Parallelize downloads
    )

    # 3. Save to CSV
    data.to_csv(INTERVALS[interval], index=True)


