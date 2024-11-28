import pandas as pd
import yfinance as yf

def load_stock_data(start_date, end_date):
    try:
        stock = yf.Ticker("AAPL")
        data = stock.history(start=start_date, end=end_date)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
