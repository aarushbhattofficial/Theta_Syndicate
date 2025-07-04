import pandas as pd
import yfinance as yf
from datetime import datetime

START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')
INTERVALS = {
    '1d': 'data/niftymicrocap250/niftymicrocap250_daily_ohlcv.csv',
    '1wk': 'data/niftymicrocap250/niftymicrocap250_weekly_ohlcv.csv',
    '1mo': 'data/niftymicrocap250/niftymicrocap250_monthly_ohlcv.csv'
}


df = pd.read_csv(r'data/niftymicrocap250/ind_niftymicrocap250list.csv')
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


