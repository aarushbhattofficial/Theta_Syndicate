import pandas as pd
import numpy as np
INTERVALS = {
    '1d': 'Theta_Syndicate/data/nifty500/nifty500_daily_ohlcv.csv',
    '1wk': 'Theta_Syndicate/data/nifty500/nifty500_weekly_ohlcv.csv',
    '1mo': 'Theta_Syndicate/data/nifty500/nifty500_monthly_ohlcv.csv'}
for index,interval in enumerate(INTERVALS):
    data=pd.read_csv(INTERVALS[interval],low_memory=False)
    df=pd.DataFrame(data)
  
  
    # Count NaNs/blanks/zeros per row (date)
    nan_counts_row = df.isna().sum(axis=1)
    blank_counts_row = (df == "").sum(axis=1)
   

# Combine all counts
    total_issue_counts_row = nan_counts_row + blank_counts_row 

# Threshold for removing rows with too many nan values
    threshold_row = 0.2 * df.shape[1]  # e.g., if 20% or more columns are bad

# Find rows (dates) to remove
    bad_rows = total_issue_counts_row[total_issue_counts_row > threshold_row].index

# Drop those rows
    df_cleaned = df.drop(index=bad_rows)
      # Count NaNs/blanks/zeros per column (stock)
    nan_counts = df_cleaned.isna().sum()
    blank_counts = (df_cleaned == "").sum()
    

# Combine all counts
    total_issue_counts = nan_counts + blank_counts  

# Find stocks to remove
    bad_stocks = total_issue_counts[total_issue_counts > 0].index

# Drop those stocks
    df_cleaned = df.drop(columns=bad_stocks)
    df_new = df_cleaned.loc[:, ~df_cleaned.columns.str.contains('^Unnamed')]
    df_new.to_csv(INTERVALS[interval],index=False)
    








