import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="AlphaScanner", layout="wide")
st.title("📈 AlphaScanner: Oversold/Overbought Dashboard")

# User Input for Watchlist
tickers = st.sidebar.text_input("Enter Tickers (comma separated)", "AAPL,TSLA,NVDA,SPY,QQQ").split(',')

def get_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df = df.join(macd)
    return df

# Main Dashboard Logic
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    ticker = ticker.strip()
    data = get_data(ticker)
    current_rsi = data['RSI'].iloc[-1]
    
    # Determine Status Color
    if current_rsi < 35:
        color = "green"
        status = "Oversold (Buy Zone)"
    elif current_rsi > 65:
        color = "red"
        status = "Overbought (Sell Zone)"
    else:
        color = "white"
        status = "Neutral"

    with st.container():
        st.subheader(f"{ticker}")
        st.metric("Current RSI", f"{current_rsi:.2f}", delta_color="normal")
        st.markdown(f"Status: :{color}[{status}]")
        
        # Plotting the Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Price"))
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)