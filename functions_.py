__all__ = [
    "Strategy",
    "clean_symbol",
    "record_monthly_weights",
    "get_rebalancing_dates",
    "backtest",
    "Backtester",
    "plot_strategy_vs_benchmark",
]

class Strategy():
    
   signalsData = signalsData = pd.read_csv(
        'auxilary/backtester_weights.csv', #replace with your file path
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
def clean_symbol(symbol):
    return symbol.replace('&', '_').replace('-', '_')  # Adjust as needed
def record_monthly_weights(weights_df, current_date, top_set):
    """
    On the rebalance date (start of month): weight = 1/N
    On the last trading day of that same month: weight = 0
    """
    if not top_set:
        return

    # 1) Compute weight
    w = 1.0 / len(top_set)

    # 2) Assign 1/N on rebalance date
    if current_date in weights_df.index:
        weights_df.loc[current_date, list(top_set)] = w

    # 3) Find the last trading day in that month
    #    Filter the index to the same year-month, then take the max date
    month = current_date.month
    year  = current_date.year

    # all dates in daily_index that match this month/year
    mask = (
        (weights_df.index.year  == year) &
        (weights_df.index.month == month)
    )
    month_dates = weights_df.index[mask]
    if month_dates.empty:
        return

    last_day = month_dates.max()

    # 4) Assign 0 on that last trading day
    weights_df.loc[last_day, list(top_set)] = 0.0
def get_rebalancing_dates(dates, frequency):
    if frequency == "weekly":
        return dates[dates.weekday == 0]  # Mondays
    elif frequency == "monthly":
        dates = dates.sort_values()
        grouped = dates.to_period("M").unique()
        first_mondays = [dates[dates.to_period("M") == period].min() for period in grouped]
        return pd.DatetimeIndex(first_mondays)
    else:
        raise ValueError("Frequency must be 'weekly' or 'monthly'.")

def backtest(start_date, end_date,z_mean, universe_name, frequency="monthly", 
             initial_capital=100000, number_stocks_active=100, 
             zscore_threshold=0.0,period=48, risk_free_rate=0.04):
    
    
    # --- 1) Read your daily trading_signals.csv to get the full daily index ---
   # Read with the first column as the index and parse it as dates
    signals_df = pd.read_csv(
    "auxilary/backtester_weights.csv",
    index_col=0,
    parse_dates=True
    )


    # This is your universe of all trading days
    daily_index = signals_df.index

    # --- 2) Pre-allocate a weights DataFrame with NaNs on that daily index ---
    weights_df = pd.DataFrame(
        data    = np.nan,
        index   = daily_index,
        columns = signals_df.columns  # all tickers in that file
    )

    z_score_period = period
    z_score_file = 'z_scores_mean.csv' if z_mean else 'z_scores.csv'
    
    # Load the universe from the CSV file
    universe_file = universe_files.get(universe_name)
    if not universe_file:
        raise ValueError(f"Invalid universe name: {universe_name}. Choose from {list(universe_files.keys())}")
    
    universe_df = pd.read_csv(universe_file)
    universe = universe_df.iloc[:, 2].tolist()  # Assuming stock symbols are in the third column
    
    # Load stock prices and z-scores
    stock_prices = pd.read_csv('split_ohlcv_data/all_close.csv', parse_dates=['Date'], index_col='Date')
    z_scores = pd.read_csv(z_score_file, parse_dates=['Date'], index_col='Date')

    # Filter valid stocks
    valid_universe = [stock+".NS" for stock in universe if stock+".NS" in stock_prices.columns]

    # Filter data based on date range
    stock_prices = stock_prices.loc[start_date:end_date, valid_universe]
    z_scores = z_scores.loc[start_date:end_date, valid_universe]

    print('Stock prices and Z-scores loaded.')
    
    portfolio_value = initial_capital
    portfolio_history = []
    dates = z_scores.index
    
    rebalancing_dates = get_rebalancing_dates(pd.to_datetime(dates), frequency)
    
    print(f"Rebalancing dates: {rebalancing_dates[-1]}")
    manual_date = pd.Timestamp('2023-12-25 00:00:00')
    rebalancing_dates = rebalancing_dates.append(pd.DatetimeIndex([manual_date]))
    rebalancing_dates = rebalancing_dates[rebalancing_dates >= dates[z_score_period]]
    portfolio_history.append({'date': rebalancing_dates[0], 'value': portfolio_value})
    prev_top_stocks = set()

    # Adjust risk-free rate based on rebalancing frequency
    periods_per_year = 52 if frequency == "weekly" else 12
    risk_free_growth_factor = (1 + risk_free_rate) ** (1 / periods_per_year)
    
    for i, current_date in enumerate(rebalancing_dates[:-1]):
        next_date = rebalancing_dates[i + 1]
        
        current_z_scores = z_scores.loc[current_date].dropna()
        
        # Select stocks above the threshold
        top_stocks = current_z_scores[current_z_scores >= zscore_threshold].nlargest(number_stocks_active).index
        
        top_set = set(top_stocks)
        retained_stocks = top_set & prev_top_stocks
        expelled_stocks = prev_top_stocks - top_set
        new_additions = top_set - prev_top_stocks

        print(f"\nRebalancing on {current_date}:")
        print(f"Qualified stocks: {list(top_stocks)}")
        print(f"Retained stocks: {list(retained_stocks)}")
        print(f"Expelled stocks: {list(expelled_stocks)}")
        print(f"New additions: {list(new_additions)}")

        prev_top_stocks = top_set

        num_selected_stocks = len(top_stocks)
        allocated_capital = portfolio_value * (num_selected_stocks / number_stocks_active)
        print(f"Allocated capital: {allocated_capital}")
        print(f"Unallocated capital: {portfolio_value - allocated_capital}")
        unallocated_capital = portfolio_value - allocated_capital

        new_portfolio_value = 0
        for stock in top_stocks:
            try:
                buy_price = stock_prices.loc[current_date, stock]
                print(f"Buying {stock} at {buy_price}")
                sell_price = stock_prices.loc[next_date, stock]
                print(f"Selling {stock} at {sell_price}")
                new_portfolio_value += (allocated_capital / num_selected_stocks) * (sell_price / buy_price)
            except KeyError:
                print(f"Skipping {stock} due to missing data.")

        # Apply risk-free growth to unallocated capital
        portfolio_value = new_portfolio_value + (unallocated_capital * 1)#risk_free_growth_factor)

        portfolio_history.append({'date': next_date, 'value': portfolio_value})
        record_monthly_weights(weights_df, current_date, top_set)

    # Log the last rebalancing selection (no return calculated)
    rebalancing_dates.normalize()
    final_date = rebalancing_dates[-1]
    print(final_date)
    final_z_scores = z_scores.loc[final_date].dropna()
    final_top_stocks = final_z_scores[final_z_scores >= zscore_threshold].nlargest(number_stocks_active).index

    final_top_set = set(final_top_stocks)
    final_retained = final_top_set & prev_top_stocks
    final_expelled = prev_top_stocks - final_top_set
    final_new = final_top_set - prev_top_stocks

    print(f"\nFinal Rebalancing on {final_date}:")
    print(f"Qualified stocks: {list(final_top_stocks)}")
    print(f"Retained stocks: {list(final_retained)}")
    print(f"Expelled stocks: {list(final_expelled)}")
    print(f"New additions: {list(final_new)}")
    weights_df.to_csv("auxilary/backtester_weights.csv", index_label="Date")
    return pd.DataFrame(portfolio_history)


class Backtester:
    def __init__(self, data: pd.DataFrame, initial_value: float):
        self.data = data
        self.portfolio_value = initial_value
        self.cash = initial_value
        self.investment = 0.0
        self.current_index = 1
        tickers = data.columns.get_level_values(0).unique()
        self.positions = pd.Series(0, index=tickers)
        self.all_positions = pd.DataFrame(columns=tickers)
        self.tradingState = {}
        self.all_signals = pd.DataFrame(columns=tickers)

    def calculate_positions(self, signal: pd.Series, value, open=True) -> pd.Series:
        if (signal < 0).any():
            raise ValueError(f'For timestamp {self.data.index[self.current_index]}, signal contains negative values: {signal[signal < 0]}')
        if not isinstance(signal, pd.Series):
            raise TypeError(f'For timestamp {self.data.index[self.current_index]}, signal must be a pandas Series, got {type(signal)}')
        if abs(signal).sum() - 1 > 1e-6:
            raise ValueError(f'For timestamp {self.data.index[self.current_index]} the sum of the abs(signals) must not be greater than 1, got {abs(signal).sum()}')

        prices = (
            self.data.xs('Open', level=1, axis=1).iloc[self.current_index]
            if open
            else self.data.xs('Close', level=1, axis=1).iloc[self.current_index]
        )
        prices = prices.reindex(signal.index)
        
        nan_index = signal.isna()
        value -= (self.positions[nan_index]*prices[nan_index]).sum()

        float_shares = (signal.replace(0,np.nan) * value) / prices.replace(0, np.nan)

        float_shares = (
            float_shares
            .replace([np.inf, -np.inf], 0)
            .fillna(0)
        )

        new_positions = pd.Series(0, index=float_shares.index, dtype=int)
        longs  = float_shares > 0
        shorts = float_shares < 0

        new_positions[longs]  = np.floor(float_shares[longs]).astype(int)
        new_positions[shorts] = np.ceil (float_shares[shorts]).astype(int)
        
        new_positions[nan_index] = self.positions[nan_index]

        return new_positions

    def calculate_cash(self, positions: pd.Series, open=True) -> float:
        index = self.current_index
        price = self.data.xs('Open',level=1,axis=1).iloc[index] if open else self.data.xs('Close',level=1,axis=1).iloc[index]
        return self.portfolio_value - (abs(positions) * price).sum()

    def update_investment(self, positions: pd.Series, new_day=False) -> float:
        index = self.current_index
        price1 = self.data.xs('Close',level=1,axis=1).iloc[index-1] if new_day else self.data.xs('Open',level=1,axis=1).iloc[index]
        price2 = self.data.xs('Open',level=1,axis=1).iloc[index] if new_day else self.data.xs('Close',level=1,axis=1).iloc[index]
        return (positions * (price2 - price1)).sum() + self.investment

    def run(self):
        processed_data = Strategy().process_data(self.data)
        self.all_positions.loc[self.data.index[0]] = self.positions
        traderData = 0
        for i in tqdm.tqdm(range(1, len(self.data))):
            self.tradingState = {
                'processed_data': processed_data[:i],
                'investment': self.investment,
                'cash': self.cash,
                'current_timestamp': self.data.index[self.current_index],
                'traderData': traderData,
                'positions': self.positions,
            }
            signal, traderData = Strategy().get_signals(self.tradingState)
            if signal is None:
                raise ValueError(f'For timestamp {self.data.index[self.current_index]}, signal is None')
            self.investment = self.update_investment(self.positions, new_day=True)
            self.portfolio_value = self.investment + self.cash
            self.positions = self.calculate_positions(signal, self.portfolio_value)
            self.cash = self.calculate_cash(self.positions)
            self.investment = self.portfolio_value - self.cash
            self.investment = self.update_investment(self.positions, new_day=False)
            self.portfolio_value = self.investment + self.cash
            self.all_positions.loc[self.data.index[i]] = self.positions
            self.all_signals.loc[self.data.index[i-1]] = signal
            self.current_index += 1

    def vectorbt_run(self):
        open_prices = self.data.xs('Open', level=1, axis=1).loc[self.all_positions.index, self.all_positions.columns]
        close_prices = self.data.xs('Close', level=1, axis=1).loc[self.all_positions.index, self.all_positions.columns]

        order_size = self.all_positions.diff().fillna(0).astype(int)
        order_size = order_size.mask(order_size == 0)

        portfolio = vbt.Portfolio.from_orders(
            close=close_prices,
            size=order_size,
            price=open_prices,
            init_cash=initial_value,
            freq='1D',
            cash_sharing=True,
            call_seq='auto',
            log=True,
        )
        
        stats_eq = portfolio.stats()
        stats_df = stats_eq.to_frame(name='Value').reset_index()
        stats_df.columns = ['Metric', 'Value']
        
        portfolio.assets().to_csv('results/assets.csv')
        portfolio.orders.records_readable.to_csv('results/log.csv')
        
        df = pd.concat([portfolio.value(),portfolio.asset_value(),portfolio.cash()], axis=1)
        df.columns = ['portfolio', 'investment', 'cash']
        df.to_csv('results/portfolio.csv')

        print(tabulate(
            stats_df,
            headers='keys',
            tablefmt='psql',
            showindex=False,
            floatfmt=".3f"
        ))
        
        return portfolio
    import matplotlib.dates as mdates
def plot_strategy_vs_benchmark(strategy_df, initial_capital=100000):
    # Load benchmark data from CSV
    benchmark_data = pd.read_csv('benchmark.csv', parse_dates=['datetime'], index_col='datetime')

    # Extract closing prices
    benchmark_data = benchmark_data[['close']]

    # Extract the start and end dates from strategy_df
    start_date = strategy_df['date'].min()
    end_date = strategy_df['date'].max()

    # Ensure benchmark_data is within the same date range
    benchmark_data = benchmark_data.loc[start_date:end_date]

    # Normalize benchmark to start with the same initial capital
    benchmark_normalized = (benchmark_data / benchmark_data.iloc[0]) * initial_capital

    # Ensure strategy_df's date column is timezone-naive
    strategy_df['date'] = pd.to_datetime(strategy_df['date'])
    strategy_df.set_index('date', inplace=True)

    # Align strategy and benchmark dates
    benchmark_normalized = benchmark_normalized.loc[strategy_df.index.min():strategy_df.index.max()]

    # Plot strategy vs benchmark
    plt.figure(figsize=(12, 6))
    plt.plot(strategy_df.index, strategy_df['value'], label='Strategy Portfolio', linewidth=2, color='blue')
    plt.plot(benchmark_normalized.index, benchmark_normalized['close'], label='NIFTY 500 (Benchmark)', linewidth=2, color='orange')
    plt.title('Portfolio Performance vs Benchmark', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Portfolio Value', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.show()