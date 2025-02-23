import pandas as pd
import datetime
from polygon.rest import RESTClient

# Hardcoded Polygon API Key
POLYGON_API_KEY = ""

class DataFetcher:
    def __init__(self, api_key=POLYGON_API_KEY):
        self.client = RESTClient(api_key)

    def get_historical_data(self, symbol, start_date, timespan="day"):
        """
        Fetches historical price data (OHLCV) from Polygon until today's date.
        """
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        bars = []
        for bar in self.client.list_aggs(symbol, 1, timespan, start_date, end_date, limit=5000):
            bars.append({
                "date": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            })

        df = pd.DataFrame(bars)
        df["date"] = pd.to_datetime(df["date"], unit='ms')
        df.set_index("date", inplace=True)
        return df

    def get_latest_price(self, symbol):
        """
        Fetches the latest trade price for a given stock symbol.
        """
        last_trade = self.client.get_last_trade(symbol)
        return last_trade.price if last_trade else None
