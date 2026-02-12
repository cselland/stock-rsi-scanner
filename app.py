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
    ticker = ticker.strip()
    data = get_data(ticker)
    
    if data is not None and 'RSI' in data.columns:
        try:
            # Drop all "NaN" values from the RSI column so we only look at real numbers
            rsi_clean = data['RSI'].dropna()
            
            if not rsi_clean.empty:
                # Grab the very last valid number
                current_rsi = float(rsi_clean.iloc[-1])

                st.subheader(f"Analysis for {ticker}")
                
                # Determine status for the UI
                if current_rsi < 30:
                    st.success(f"🔥 OVERSOLD: {current_rsi:.2f}")
                elif current_rsi > 70:
                    st.error(f"⚠️ OVERBOUGHT: {current_rsi:.2f}")
                else:
                    st.info(f"Neutral: {current_rsi:.2f}")
                
                # Plotting
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Price"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Not enough data to calculate RSI for {ticker} yet.")
        
        except Exception as e:
            st.error(f"Error displaying {ticker}: {e}")
    else:
        st.error(f"Ticker {ticker} not found or data is empty.")
