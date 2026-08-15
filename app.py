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
symbol = st.sidebar.selectbox("Symbol", ["
