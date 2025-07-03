import numpy as np 
import pandas as pd

# Read your signals CSV, assuming the first column is 'date'
portfolio_signals_df = pd.read_csv(r'auxilary/trading_signals.csv', index_col=0, parse_dates=True)
max_positions = 10  # change accordingly

def calculate_weights(signals_df, max_positions):
    current_positions = set()  # Track held tickers
    weights_history = [] 

    for date in signals_df.index:
        signals = signals_df.loc[date]
        weights = pd.Series(np.nan, index=signals.index)

        # Error check: -1 on first date
        if date == signals_df.index[0] and (signals == -1).any():
            raise ValueError(f"-1 (exit) signal on first date for: {signals[signals == -1].index.tolist()}")

        # Handle exits: set weight to 0, remove from current_positions
        for ticker in list(current_positions):
            if signals[ticker] == -1:
                weights[ticker] = 0
                current_positions.remove(ticker)

        # For new entries (signal 1 and not already held), assign dynamic weights
        new_entries = [ticker for ticker in signals.index if signals[ticker] == 1 and ticker not in current_positions]
        available_slots = max_positions - len(current_positions)
        slots_to_use = min(len(new_entries), available_slots)
        if slots_to_use > 0:
            dynamic_weight = 1 / slots_to_use
            for ticker in new_entries[:slots_to_use]:
                weights[ticker] = dynamic_weight
                current_positions.add(ticker)
            print(slots_to_use, " slots used on ", date)
        else: 
            print("no slots available on ", date)

        # For tickers with signal -1 that are not in current_positions (shouldn't happen, but for completeness)
        for ticker in signals.index:
            if signals[ticker] == -1 and ticker not in current_positions:
                weights[ticker] = 0

        weights_history.append(weights)

    weights_df = pd.DataFrame(weights_history, index=signals_df.index)
    return weights_df

calculated_weights_df = calculate_weights(portfolio_signals_df, max_positions=10)
calculated_weights_df.to_csv('auxilary/backtester_weights.csv')
