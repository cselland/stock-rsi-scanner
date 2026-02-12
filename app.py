import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="AlphaScanner Pro", layout="wide")

# 1. ROBUST DATA FETCHING
def get_data(ticker):
    ticker = ticker.strip()
    # 1y period ensures the 14-day RSI 'warm-up' is complete
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    
    if df.empty or len(df) < 20:
        return None

    df['RSI'] = ta.rsi(df['Close'], length=14)
    # Adding MACD for confirmation
    macd = ta.macd(df['Close'])
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
    return df

# 2. VANGUARD & MARKET LISTS
VANGUARD_LIST = [
    'VTI', 'VOO', 'VUG', 'VTV',  # Total Market, S&P 500, Growth, Value
    'VXUS', 'VWO',               # International & Emerging Markets
    'VNQ', 'VGT', 'VHT', 'VDE',  # Real Estate, Tech, Health, Energy
    'VCR', 'VDC', 'VPU', 'VAW'   # Consumer Disc, Staples, Utilities, Materials
]
MARKET_ETFS = ['SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLK', 'XLE']

# 3. SIDEBAR CONTROLS
st.sidebar.title("🔍 Scanner Settings")
scan_type = st.sidebar.selectbox("Choose Scan Group", ["Vanguard ETFs", "Standard Sector ETFs", "Custom Watchlist"])
manual_tickers = st.sidebar.text_input("Manual Tickers (for Watchlist)", "AAPL,TSLA,NVDA")
run_scan = st.sidebar.button("Run Scanner")

# 4. SCANNER LOGIC
if run_scan:
    # Determine which list to use
    selected_list = VANGUARD_LIST if scan_type == "Vanguard ETFs" else MARKET_ETFS
    if scan_type == "Custom Watchlist":
        selected_list = manual_tickers.split(',')

    st.header(f"⚡ {scan_type} Opportunities")
    cols = st.columns(4) # 4-column layout for Vanguard list
    col_idx = 0
    found_any = False
    
    with st.spinner(f'Scanning {len(selected_list)} tickers...'):
        for ticker in selected_list:
            data = get_data(ticker)
            if data is not None:
                rsi_vals = data['RSI'].dropna()
                if not rsi_vals.empty:
                    current_rsi = float(rsi_vals.iloc[-1])
                    
                    # Highlight if RSI is hitting extreme levels
                    if current_rsi < 35 or current_rsi > 65:
                        found_any = True
                        with cols[col_idx % 4]:
                            status = "🟢 OVERSOLD" if current_rsi < 35 else "🔴 OVERBOUGHT"
                            st.metric(ticker, f"{current_rsi:.2f}", status)
                            
                            # Small trend chart for each hit
                            st.line_chart(data['Close'].tail(30), height=100)
                        col_idx += 1
        
    if not found_any:
        st.write("No extreme RSI levels found in this group right now.")
    st.divider()

# 5. GENERAL WATCHLIST VIEW
st.header("📋 Live Watchlist")
for t in manual_tickers.split(','):
    data = get_data(t)
    if data is not None:
        rsi_vals = data['RSI'].dropna()
        if not rsi_vals.empty:
            curr_rsi = float(rsi_vals.iloc[-1])
            st.write(f"**{t.strip().upper()}** | RSI: `{curr_rsi:.2f}`")
