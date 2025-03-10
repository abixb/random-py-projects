# This is the GUI version of the stock ticker built with tkinter.

# $HOOD and $ACHR are hard-coded.

#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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

def get_stock_info():
    """
    Fetch stock information for hardcoded tickers and format it.
    """
    tickers = ['HOOD', 'ACHR']
    results = []
    for ticker in tickers:
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            formatted_volume = format_volume(stock_data['Volume'])
            result = f"--- {ticker} Stock Data ---\n"
            result += f"Date:   {stock_data['Date']}\n"
            result += f"Open:   {stock_data['Open']:.2f}\n"
            result += f"High:   {stock_data['High']:.2f}\n"
            result += f"Low:    {stock_data['Low']:.2f}\n"
            result += f"Close:  {stock_data['Close']:.2f}\n"
            result += f"Volume: {formatted_volume}\n\n"
            results.append(result)
        else:
            results.append(f"No data found for ticker: {ticker}\n\n")
    return "".join(results)

def on_fetch_button_click():
    """
    Called when the button is clicked; fetches the data and displays it.
    """
    text_area.delete('1.0', tk.END)
    try:
        data = get_stock_info()
        text_area.insert(tk.END, data)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Stock Data Fetcher")

# Create a frame for the button
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

fetch_button = ttk.Button(frame, text="Fetch Stock Data", command=on_fetch_button_click)
fetch_button.grid(row=0, column=0, padx=5, pady=5)

# Create a scrolled text area to display the stock data
text_area = scrolledtext.ScrolledText(root, width=50, height=15, wrap=tk.WORD)
text_area.grid(row=1, column=0, padx=10, pady=10)

root.mainloop()
