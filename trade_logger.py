import pandas as pd

class TradeLogger:
    @staticmethod
    def save_trades(trades, filename):
        df = pd.DataFrame(trades)
        df.to_csv(filename, index=False)
