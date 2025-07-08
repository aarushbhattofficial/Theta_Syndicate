import pandas as pd
import yfinance as yf
from datetime import datetime

START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')
INTERVALS = {
    '1d': 'Theta_Syndicate/data/nifty500/nifty500_daily_ohlcv.csv',
    '1wk': 'Theta_Syndicate/data/nifty500/nifty500_weekly_ohlcv.csv',
    '1mo': 'Theta_Syndicate/data/nifty500/nifty500_monthly_ohlcv.csv'
}


df = pd.read_csv(r'Theta_Syndicate/data/nifty500/ind_nifty500list.csv')
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


