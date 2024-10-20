
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time

def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def get_latest_price(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1d')
    return hist['Close'].iloc[-1] if not hist.empty else None

def get_180day_annualized_std_dev(hist):
    if not hist.empty:
        daily_returns = hist['Close'].pct_change().dropna()
        annualized_std = np.std(daily_returns) * np.sqrt(252) * 100
        return min(annualized_std, 100)
    return None

def get_simple_total_return_last_month(hist):
    if not hist.empty and len(hist) >= 30:
        last_month_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[-30] - 1) * 100
        return last_month_return
    return None

def get_last_12_months_total_return(hist):
    if not hist.empty:
        return (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
    return None

def get_sp500_last_12_months_return():
    sp500 = yf.Ticker('^GSPC')
    hist = sp500.history(period='1y')
    if not hist.empty:
        return (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
    return None

def get_all_metrics(tickers):
    sp500_return = get_sp500_last_12_months_return()
    
    results = []
    total_tickers = len(tickers)
    
    for i, ticker in enumerate(tickers, 1):
        try:
            stock_data = get_stock_data(ticker, period='1y')
            
            if stock_data.empty:
                print(f"Skipping {ticker} due to insufficient data")
                continue

            latest_price = stock_data['Close'].iloc[-1]
            std_dev = get_180day_annualized_std_dev(stock_data.tail(126))  # 126 trading days ~ 6 months
            last_month_return = get_simple_total_return_last_month(stock_data)
            last_12_months_return = get_last_12_months_total_return(stock_data)
            
            if latest_price is None or std_dev is None or last_month_return is None or last_12_months_return is None:
                print(f"Skipping {ticker} due to insufficient data")
                continue
            
            excess_return = last_12_months_return - sp500_return if sp500_return is not None else None

            results.append({
                'Ticker': ticker,
                'Latest Price': latest_price,
                '180-Day Annualized Std Dev': std_dev,
                'Simple Total Return (USD) Last Month': last_month_return,
                'Last 12 Months Total Return': last_12_months_return,
                'Last 12 Months S&P 500 Total Return': sp500_return,
                'Last 12 Month Excess Return': excess_return,
                '22D ADV ($MM)': (stock_data['Volume'].rolling(22).mean() * stock_data['Close'].rolling(22).mean()).iloc[-1] / 1e6,
                '10D ADV ($MM)': (stock_data['Volume'].rolling(10).mean() * stock_data['Close'].rolling(10).mean()).iloc[-1] / 1e6,
                '10D ADV Shares (MM)': stock_data['Volume'].rolling(10).mean().iloc[-1] / 1e6,
                '22D ADV Shares (MM)': stock_data['Volume'].rolling(22).mean().iloc[-1] / 1e6,
            })
            
            print(f"Processed {i}/{total_tickers}: {ticker}")
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
        
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    from app import get_tickers  # Import function from app.py
    
    tickers = get_tickers()
    if tickers:
        result_df = get_all_metrics(tickers)
        
        # Save results to CSV
        result_df.to_csv('stock_metrics.csv', index=False)
        print("Results saved to stock_metrics.csv")
    else:
        print("No tickers found. Please run the Streamlit app first to fetch stock data.")
