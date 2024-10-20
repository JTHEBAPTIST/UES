
import logging
from finvizfinance.screener.overview import Overview
import pandas as pd
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FILTERS = {
    'Price': 'Over $5',
    'Market Cap.': '+Mid (over $2bln)',
    'Country': 'USA',
    'Industry': 'Stocks only (ex-Funds)',
}

PARAMETERS = [
    'Ticker', 'Exchange', 'Index', 'Sector', 'Industry', 'Country', 'Market Cap.',
    'P/E', 'Forward P/E', 'PEG', 'P/S', 'P/B', 'Price/Cash', 'Price/Free Cash Flow',
    # More parameters can be added here
]

def get_stocks() -> pd.DataFrame:
    """
    Fetches stock data based on filters and returns it as a DataFrame.
    """
    foverview = Overview()

    try:
        foverview.set_filter(filters_dict=FILTERS)
        df_overview = foverview.screener_view(columns=PARAMETERS)
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        return pd.DataFrame()

    return df_overview

def get_tickers():
    """
    Retrieves the list of tickers from the most recent stock data.
    """
    df_stocks = get_stocks()
    if not df_stocks.empty and 'Ticker' in df_stocks.columns:
        return df_stocks['Ticker'].tolist()
    else:
        logger.warning("No tickers found or 'Ticker' column missing.")
        return []

def main():
    st.title("Stock Screener App")
    st.write("This app retrieves stocks based on filters and displays them.")

    # Add filter description
    st.sidebar.header('Filters')
    selected_price = st.sidebar.selectbox('Price', ['Over $5', 'Over $10', 'Over $20'])
    selected_market_cap = st.sidebar.selectbox('Market Cap', ['+Mid (over $2bln)', '+Large (over $10bln)'])

    FILTERS['Price'] = selected_price
    FILTERS['Market Cap.'] = selected_market_cap

    if st.button('Get Stocks'):
        df_stocks = get_stocks()

        if not df_stocks.empty:
            st.success(f"Retrieved {len(df_stocks)} stocks")
            st.dataframe(df_stocks)

            # Allow downloading as CSV
            csv = df_stocks.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name='Overview.csv', mime='text/csv')
        else:
            st.error("No data retrieved. Try changing filters.")

if __name__ == "__main__":
    main()
