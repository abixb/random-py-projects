# This is a simple stock ticker -- custom crafted for the stocks I hold, using Yahoo Finance APIs

#!/usr/bin/env python3
import yfinance as yf

def format_volume(volume):
    """
    Format the volume number into a human-friendly string.
    E.g., 1500 becomes '1.50K', 2500000 becomes '2.50M'
    """
    if volume < 1e3:
        return str(volume)
    elif volume < 1e6:
        return f"{volume/1e3:.2f}K"
    elif volume < 1e9:
        return f"{volume/1e6:.2f}M"
    else:
        return f"{volume/1e9:.2f}B"

def fetch_stock_data(ticker):
    """
    Fetch the latest one-day stock data for a given ticker.
    Returns a dictionary with the date and key price data if available.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    if data.empty:
        return None
    last_row = data.iloc[-1]
    return {
        'Date': last_row.name.date(),
        'Open': last_row['Open'],
        'High': last_row['High'],
        'Low': last_row['Low'],
        'Close': last_row['Close'],
        'Volume': int(last_row['Volume'])
    }

def main():
    tickers = ['HOOD', 'ACHR']
    for ticker in tickers:
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            formatted_volume = format_volume(stock_data['Volume'])
            print(f"--- {ticker} Stock Data ---")
            print(f"Date:   {stock_data['Date']}")
            print(f"Open:   {stock_data['Open']:.2f}")
            print(f"High:   {stock_data['High']:.2f}")
            print(f"Low:    {stock_data['Low']:.2f}")
            print(f"Close:  {stock_data['Close']:.2f}")
            print(f"Volume: {formatted_volume}\n")
        else:
            print(f"No data found for ticker: {ticker}\n")

if __name__ == '__main__':
    main()
