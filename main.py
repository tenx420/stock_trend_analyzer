import datetime
from data_fetcher import DataFetcher
from indicators import Indicators
from trade_simulator import TradeSimulator
from trade_logger import TradeLogger
from dashboard import Dashboard

# Define multiple tickers
tickers = ["AAPL", "TSLA", "GOOG", "AMZN", "MSFT", "NFLX", "NVDA", "SPY", "QQQ","GLD","SLV"]

START_DATE = "2023-01-01"
END_DATE = datetime.datetime.today().strftime("%Y-%m-%d")

fetcher = DataFetcher()
results = {}

for ticker in tickers:
    print(f"Processing {ticker} ...")
    df = fetcher.get_historical_data(ticker, START_DATE)
    if df.empty:
        print(f"No data returned for {ticker}. Skipping.")
        continue

    # Compute Indicators
    df = Indicators.compute_sma(df, 50)
    df = Indicators.compute_sma(df, 200)
    df = Indicators.compute_rsi(df, 14)
    df = Indicators.compute_macd(df)

    # Simulate Strategy
    simulator = TradeSimulator(initial_balance=1000)
    trades, in_progress_trade, balance = simulator.simulate_trades(df)

    # Save trade history
    TradeLogger.save_trades(trades, filename=f"logs/{ticker}_trade_history.csv")

    # ---- Buy & Hold Calculation ----
    # Buy shares at the first available close price
    bnh_start_price = df.iloc[0]["close"]
    bnh_end_price   = df.iloc[-1]["close"]
    bnh_shares = 1000 / bnh_start_price
    bnh_final_balance = bnh_shares * bnh_end_price

    results[ticker] = {
        "df": df,
        "trades": trades,
        "in_progress_trade": in_progress_trade,
        "balance": balance,
        "bnh_final_balance": bnh_final_balance  # We'll do P/L in the dashboard
    }

# 1) Print console summary
Dashboard.display_portfolio(results)

# 2) Plot charts
Dashboard.plot_portfolio_charts(results)

# 3) Create HTML dashboard (Strategy vs. Buy & Hold)
Dashboard.create_html_dashboard(results, START_DATE, END_DATE, output_file="dashboard.html")

