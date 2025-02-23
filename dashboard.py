import pandas as pd
import matplotlib.pyplot as plt
import os
import webbrowser

class Dashboard:
    @staticmethod
    def display_portfolio(results):
        """
        Print a console summary (unchanged).
        """
        for ticker, data in results.items():
            print(f"\n=== {ticker} ===")
            trades = data["trades"]
            in_progress_trade = data["in_progress_trade"]
            balance = data["balance"]
            df_trades = pd.DataFrame(trades)
            print("Trade History:")
            print(df_trades)
            if in_progress_trade:
                print("In-progress Trade:")
                print(f"  Entry Date: {in_progress_trade['entry_date']}, Entry Price: {in_progress_trade['entry_price']:.2f}")
                print(f"  Shares: {in_progress_trade['shares']:.4f}, Stop Loss: {in_progress_trade['stop_loss']:.2f}")
                print(f"  Target Price: {in_progress_trade['target_price']:.2f}, Current Price: {in_progress_trade.get('latest_price', 0):.2f}")
                print(f"  Unrealized P/L: {in_progress_trade.get('profit_loss', 0):.2f}")
                print(f"  Unrealized P/L%: {in_progress_trade.get('profit_loss_pct', 0):.2f}%")
            else:
                print("No active trades.")
            print(f"Available Balance: ${balance:.2f}")

    @staticmethod
    def plot_portfolio_charts(results):
        """
        Plot charts for each ticker in /charts folder.
        """
        os.makedirs("charts", exist_ok=True)
        for ticker, data in results.items():
            df = data["df"]
            trades = data["trades"]
            in_progress_trade = data["in_progress_trade"]

            plt.figure(figsize=(12,6))
            plt.plot(df.index, df["close"], label="Price", color="black")
            plt.plot(df.index, df["SMA50"], label="SMA50", color="blue")
            plt.plot(df.index, df["SMA200"], label="SMA200", color="red")
            
            for trade in trades:
                plt.scatter(trade["entry_date"], trade["entry_price"], marker="^", color="green", label="Buy")
                if "exit_date" in trade:
                    plt.scatter(trade["exit_date"], trade["exit_price"], marker="v", color="red", label="Sell")
            
            if in_progress_trade:
                plt.scatter(in_progress_trade["entry_date"], in_progress_trade["entry_price"], 
                            marker="^", color="orange", label="In-progress")
            
            plt.title(f"{ticker} Price with Trades")
            plt.legend()
            valid_date = df.index[-1].strftime("%Y-%m-%d")
            file_path = f"charts/{ticker}_{valid_date}_chart.png"
            plt.savefig(file_path)
            print(f"Chart saved for {ticker} at: {file_path}")
            plt.show()

    @staticmethod
    def create_html_dashboard(results, start_date, end_date, output_file="dashboard.html"):
        """
        Creates an HTML dashboard with:
          - Start & End date of backtest
          - In-Progress Trades table
          - Completed Trades table (Strategy vs. Buy & Hold)
        """
        html = "<html><head><title>Trading Dashboard</title>"
        html += """
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; }
            table { width: 90%; margin-bottom: 20px; }
            h1, h2 { color: #333; }
        </style>
        """
        html += "</head><body>"
        html += "<h1>Trading Dashboard</h1>"

        # Show start/end date
        html += f"<p>Backtest from <b>{start_date}</b> to <b>{end_date}</b></p>"

        # In-Progress Trades Table
        html += "<h2>In-Progress Trades</h2>"
        html += "<table><tr>"
        html += "<th>Ticker</th><th>Entry Date</th><th>Entry Price</th><th>Current Price</th>"
        html += "<th>Shares</th><th>Unrealized P/L</th><th>Unrealized P/L%</th>"
        html += "<th>Stop Loss</th><th>Target Price</th></tr>"
        
        for ticker, data in results.items():
            in_progress = data["in_progress_trade"]
            if in_progress:
                unreal_pnl = in_progress.get("profit_loss", 0)
                unreal_pnl_pct = in_progress.get("profit_loss_pct", 0)
                current_price = in_progress.get("latest_price", 0)
                html += f"<tr><td>{ticker}</td>"
                html += f"<td>{in_progress['entry_date']}</td>"
                html += f"<td>{in_progress['entry_price']:.2f}</td>"
                html += f"<td>{current_price:.2f}</td>"
                html += f"<td>{in_progress['shares']:.4f}</td>"
                html += f"<td>{unreal_pnl:.2f}</td>"
                html += f"<td>{unreal_pnl_pct:.2f}%</td>"
                html += f"<td>{in_progress['stop_loss']:.2f}</td>"
                html += f"<td>{in_progress['target_price']:.2f}</td>"
                html += "</tr>"
        html += "</table>"

        # Completed Trades - Compare Strategy vs. Buy & Hold
        html += "<h2>Completed Trades - Final Profit/Loss vs. Buy & Hold</h2>"
        html += """
        <table>
          <tr>
            <th>Ticker</th>
            <th>Strategy Final Balance</th>
            <th>Strategy P/L</th>
            <th>Strategy P/L%</th>
            <th>BnH Final Balance</th>
            <th>BnH P/L</th>
            <th>BnH P/L%</th>
          </tr>
        """

        for ticker, data in results.items():
            # Strategy Results
            strategy_balance = data["balance"]
            strategy_pl = strategy_balance - 1000
            strategy_pl_pct = (strategy_pl / 1000) * 100

            # Buy & Hold Calculation
            bnh_final_balance = data["bnh_final_balance"]
            bnh_pl = bnh_final_balance - 1000
            bnh_pl_pct = (bnh_pl / 1000) * 100

            # If there's an in-progress trade, the strategy is not "completed" yet,
            # but we can still show the current strategy balance vs. BnH
            html += f"<tr><td>{ticker}</td>"
            html += f"<td>{strategy_balance:.2f}</td>"
            html += f"<td>{strategy_pl:.2f}</td>"
            html += f"<td>{strategy_pl_pct:.2f}%</td>"
            html += f"<td>{bnh_final_balance:.2f}</td>"
            html += f"<td>{bnh_pl:.2f}</td>"
            html += f"<td>{bnh_pl_pct:.2f}%</td>"
            html += "</tr>"

        html += "</table>"
        html += "</body></html>"

        with open(output_file, "w") as f:
            f.write(html)
        print(f"HTML dashboard created at: {output_file}")

        # Automatically open in default browser
        webbrowser.open("file://" + os.path.realpath(output_file))
        return output_file


