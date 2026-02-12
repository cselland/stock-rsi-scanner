import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go

yf.set_tz_cache(False) # Prevents some common timezone errors

# 1. THE REFRESHED FUNCTION
def get_data(ticker):
    ticker = ticker.strip()
    # Download data
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    
    if df.empty:
        return None

    # Calculate RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Calculate MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    
    # THE FIX: Safely combine the data
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
        
    return df

# 2. THE USER INTERFACE
st.title("📈 AlphaScanner")
tickers_input = st.sidebar.text_input("Enter Tickers (comma separated)", "AAPL,TSLA,NVDA")
tickers = tickers_input.split(',')

# 3. THE DISPLAY LOGIC
for ticker in tickers:
    data = get_data(ticker)
    
    # Check if data exists and RSI was calculated
    if data is not None and 'RSI' in data.columns:
        # THE FIX: .iloc[-1] gets the last row, 
        # .item() ensures it's a single number, not a "Series"
        try:
            last_row_rsi = data['RSI'].iloc[-1]
            
            # Handle cases where yfinance returns a multi-index Series
            if isinstance(last_row_rsi, pd.Series):
                current_rsi = float(last_row_rsi.iloc[0])
            else:
                current_rsi = float(last_row_rsi)

            st.subheader(f"Analysis for {ticker}")
            
            # Check if current_rsi is a valid number (not NaN)
            if pd.isna(current_rsi):
                st.warning(f"RSI for {ticker} is currently calculating... (Need more data)")
            else:
                st.write(f"Current RSI: {current_rsi:.2f}")
        
        except Exception as e:
            st.error(f"Error displaying RSI for {ticker}: {e}")
        
        # Simple Price Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Price"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Could not find data for {ticker}")
