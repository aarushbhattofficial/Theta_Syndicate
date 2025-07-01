import pandas as pd
from typing import Tuple
import numpy as np

class Strategy():
    
   signalsData = signalsData = pd.read_csv(
        'daily_signals.csv', #replace with your file path
        na_values=['nan', 'NaN', ''],
        keep_default_na=True
    )
   signalsData.set_index(signalsData.columns[0], inplace=True)
   
   def process_data(self, data) -> pd.DataFrame:
      return data

   def get_signals(self, tradingState: dict) -> Tuple[list, str]:

      signal = Strategy.signalsData.iloc[tradingState['traderData']]
      tickers = signal.index.tolist()
      signal = pd.Series(signal.values, index=tickers)
      traderData = tradingState['traderData'] + 1
   
      return signal, traderData
   
   
# class Strategy():
   
#    def process_data(self, data) -> pd.DataFrame:
#       return data

#    def get_signals(self, tradingState: dict) -> Tuple[list, str]:

#       tickers = tradingState['positions'].index
      
#       # Create equal weight signals for all stocks
#       num_tickers = len(tickers)
#       signal = pd.Series(np.nan, index=tickers)  # Initialize with NaN
      
#       if int(tradingState['traderData'])%14 == 0:
#          signal = pd.Series([np.nan]*(num_tickers-2) + [0.0,1.0], index=tickers) # Equal weight for each stock
#       elif int(tradingState['traderData'])%3 == 0:
#          signal = pd.Series(1 / num_tickers, index=tickers)
         
#       signal = pd.Series(1 / num_tickers, index=tickers)
#       traderData = int(tradingState['traderData']) + 1
#       # Trader data can be updated or left as an empty string
      
#       return signal, traderData