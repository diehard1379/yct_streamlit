import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ================================================
# 1) FETCH DATA FROM BINANCE
# ================================================
def fetch_klines(symbol="BTCUSDT", interval="1h", limit=300):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params)

    if r.status_code != 200:
        st.error("❌ Error fetching data from Binance")
        return None

    raw = r.json()
    data = []

    for k in raw:
        data.append({
            "time": pd.to_datetime(k[0], unit="ms"),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })

    return pd.DataFrame(data)

# ================================================
# 2) INDICATORS
# ================================================
def add_indicators(df):
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()
    df["RSI"] = compute_rsi(df["close"])
    df["MACD"], df["Signal"], df["Histogram"] = compute_macd(df["close"])
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_macd(series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

# ================================================
# 3) STREAMLIT UI
# ================================================
st.set_page_config(page_title="YCT Crypto Dashboard", layout="wide")

st.title("📊 YCT Crypto Dashboard")
st.write("Live Binance Data + Indicators + Professional Charts")

# Sidebar
symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "4h", "1d"])
limit = st.sidebar.slider("Candles", 100, 500, 300)

# Fetch data
df = fetch_klines(symbol, interval, limit)

if df is None:
    st.stop()

df = add_indicators(df)

# ================================================
# 4) MAIN CHART (CANDLE + MA + VOLUME)
# ================================================
fig = go.Figure()

# Candles
fig.add_trace(go.Candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="Price"
))

# MA20
fig.add_trace(go.Scatter(
    x=df["time"], y=df["MA20"],
    line=dict(color="yellow", width=1.5),
    name="MA20"
))

# MA50
fig.add_trace(go.Scatter(
    x=df["time"], y=df["MA50"],
    line=dict(color="cyan", width=1.5),
    name="MA50"
))

# Volume Bars
fig.add_trace(go.Bar(
    x=df["time"],
    y=df["volume"],
    name="Volume",
    marker_color="rgba(0,150,255,0.4)",
    yaxis="y2"
))

fig.update_layout(
    height=600,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    yaxis=dict(title="Price"),
    yaxis2=dict(title="Volume", overlaying="y", side="right")
)

st.subheader("📈 Price Chart")
st.plotly_chart(fig, use_container_width=True)

# ================================================
# 5) RSI CHART
# ================================================
st.subheader("RSI Indicator")
st.line_chart(df["RSI"])

# ================================================
# 6) MACD CHART
# ================================================
macd_fig = go.Figure()

macd_fig.add_trace(go.Scatter(
    x=df["time"], y=df["MACD"],
    line=dict(color="orange"),
    name="MACD"
))

macd_fig.add_trace(go.Scatter(
    x=df["time"], y=df["Signal"],
    line=dict(color="blue"),
    name="Signal"
))

macd_fig.add_trace(go.Bar(
    x=df["time"], y=df["Histogram"],
    name="Histogram",
    ma
