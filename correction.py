import pandas as pd
import os

INTERVALS = {
    '1d': 'Theta_Syndicate/data/nifty500/nifty500_daily_ohlcv.csv',
    '1wk': 'Theta_Syndicate/data/nifty500/nifty500_weekly_ohlcv.csv',
    '1mo': 'Theta_Syndicate/data/nifty500/nifty500_monthly_ohlcv.csv'
}
for interval in INTERVALS:
   destination=INTERVALS[interval]
   data=pd.read_csv(destination )
   df=pd.DataFrame(data)
   
   df.columns = df.columns.str.replace(r'\.\d+$', '', regex=True)
    
   
    
    # If you want, save it back:
   df.to_csv(destination, index=False)
         

