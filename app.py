import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go

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
    
    if data is not None and 'RSI' in data.columns:
        current_rsi = data['RSI'].iloc[-1]
        st.subheader(f"Analysis for {ticker}")
        st.write(f"Current RSI: {current_rsi:.2f}")
        
        # Simple Price Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Price"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Could not find data for {ticker}")
