# Project Structure

### fetch_data.py
Generates csv files for daily, weekly and monthly data from the list of stocks given in ind_nifty500list.csv

### signal_generator.py
Generates trading_signals.csv from ohlcv csv file to be fed into trading_signals_to_weights.py

### strategy.py
Module containing strategies to be employed by calling the corresponding function in signal_generator.py

### trading_signals_to_weights.py
Generates backtester_weights.csv from trading_signals.csv to be fed into backtester

### data folder
Contains all the data files - daily, weekly, monthly ohlcv

### auxilary folder
Contains trading_signals.csv and backtester_weights.csv

### requirements.txt
List of all packages used in the project. After activating the virtual environment you are using for the project, run the following command in the terminal to install all the required packages. \
_pip install -r requirements.txt_

### .gitignore
List of files not tracked by github. For instance, the .DS_Store file generated in MacOS. Ensures cross-system compatibility while working on the same repository.
