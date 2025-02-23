import logging
import datetime

logging.basicConfig(filename="logs/trades.log", level=logging.INFO)

class TradeSimulator:
    def __init__(self, initial_balance=1000, stop_loss_pct=0.02, target_pct=0.05):
        self.stop_loss_pct = stop_loss_pct
        self.target_pct = target_pct
        self.trades = []
        self.current_position = None
        self.balance = initial_balance
        self.in_progress_trade = None

    def simulate_trades(self, df):
        for index, row in df.iterrows():
            price = row["close"]
            date = index.date()

            # ENTRY Condition: (Example) SMA50 > SMA200 and RSI < 30
            if (not self.current_position) and (row["SMA50"] > row["SMA200"]) and (row["RSI"] < 30):
                cost = self.balance
                shares = cost / price
                self.balance -= cost  # Deduct cost immediately

                self.current_position = {
                    "entry_date": date,
                    "entry_price": price,
                    "shares": shares,
                    "stop_loss": price * (1 - self.stop_loss_pct),
                    "target_price": price * (1 + self.target_pct),
                    "status": "OPEN",
                    "cost_of_trade": cost  # for calculating P/L%
                }
                logging.info(f"BUY {shares:.4f} shares at {price:.2f} on {date}")
                self.in_progress_trade = self.current_position

            # EXIT Conditions: stop-loss or target
            if self.current_position:
                if price <= self.current_position["stop_loss"]:
                    profit_loss = (price - self.current_position["entry_price"]) * self.current_position["shares"]
                    self.balance += self.current_position["shares"] * price
                    self.trades.append({
                        **self.current_position,
                        "exit_date": date,
                        "exit_price": price,
                        "profit_loss": profit_loss,
                        "status": "CLOSED",
                        "reason": "STOP-LOSS"
                    })
                    logging.info(f"STOP-LOSS hit at {price:.2f} on {date}, P/L: {profit_loss:.2f}")
                    self.current_position = None
                    self.in_progress_trade = None

                elif price >= self.current_position["target_price"]:
                    profit_loss = (price - self.current_position["entry_price"]) * self.current_position["shares"]
                    self.balance += self.current_position["shares"] * price
                    self.trades.append({
                        **self.current_position,
                        "exit_date": date,
                        "exit_price": price,
                        "profit_loss": profit_loss,
                        "status": "CLOSED",
                        "reason": "TARGET HIT"
                    })
                    logging.info(f"TARGET reached at {price:.2f} on {date}, P/L: {profit_loss:.2f}")
                    self.current_position = None
                    self.in_progress_trade = None

        # If there's an open trade, update it with the latest price
        if self.current_position:
            latest_price = df.iloc[-1]["close"]
            cost_of_trade = self.current_position["cost_of_trade"]
            self.current_position["latest_price"] = latest_price
            self.current_position["profit_loss"] = (latest_price - self.current_position["entry_price"]) * self.current_position["shares"]
            self.current_position["profit_loss_pct"] = (self.current_position["profit_loss"] / cost_of_trade) * 100
            self.in_progress_trade = self.current_position

        return self.trades, self.in_progress_trade, self.balance

