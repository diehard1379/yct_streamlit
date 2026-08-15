import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ================================================
# FETCH DATA
# ================================================
def fetch_klines(symbol="BTCUSDT", interval="1h", limit=300):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params)

    if r.status_code != 200:
        st.error("Error fetching data")
        return None

    raw = r.json()
    data = []

    for k in raw:
        data.append({
            "time": pd.to_datetime(k[0], unit="ms"),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4])
        })

    return pd.DataFrame(data)

# ================================================
# SIMPLE ZIGZAG SWING DETECTION
# ================================================
def zigzag(df, deviation=3):
    swings = []
    last_pivot = df["close"].iloc[0]
    last_type = None

    for i in range(1, len(df)):
        price = df["close"].iloc[i]

        if last_type != "high" and price >= last_pivot * (1 + deviation/100):
            swings.append(("high", df["time"].iloc[i], price))
            last_pivot = price
            last_type = "high"

        elif last_type != "low" and price <= last_pivot * (1 - deviation/100):
            swings.append(("low", df["time"].iloc[i], price))
            last_pivot = price
            last_type = "low"

    return swings

# ================================================
# YTC METRICS
# ================================================
def compute_projection(swings):
    values = []
    for i in range(1, len(swings)):
        prev = swings[i-1][2]
        curr = swings[i][2]
        values.append(abs(curr - prev))
    return values

def compute_depth(swings):
    return compute_projection(swings)

def compute_momentum(df):
    return df["close"].diff().abs().rolling(5).mean()

def compute_acceleration(df):
    return df["close"].diff().diff()

# ================================================
# STREAMLIT UI
# ================================================
st.set_page_config(page_title="YTC Price Action Dashboard", layout="wide")

st.title("📊 YTC Price Action Dashboard (Lance Beggs)")
st.write("Pure price action. No indicators. Only YTC logic.")

symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT"])
interval = st.sidebar.selectbox("Interval", ["1h", "4h", "1d"])
limit = st.sidebar.slider("Candles", 100, 500, 300)

df = fetch_klines(symbol, interval, limit)

if df is None:
    st.stop()

# Compute swings
swings = zigzag(df)

# Compute YTC metrics
projection = compute_projection(swings)
depth = compute_depth(swings)
momentum = compute_momentum(df)
acceleration = compute_acceleration(df)

# ================================================
# CHART
# ================================================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="Price"
))

# Plot swings
for s in swings:
    fig.add_trace(go.Scatter(
        x=[s[1]],
        y=[s[2]],
        mode="markers",
        marker=dict(size=8, color="yellow"),
        name=f"{s[0]} swing"
    ))

fig.update_layout(
    height=600,
    template="plotly_dark",
    xaxis_rangeslider_visible=False
)

st.subheader("Price + Swings")
st.plotly_chart(fig, use_container_width=True)

# ================================================
# METRICS
# ================================================
st.subheader("YTC Metrics")

st.write("Projection:", projection[-5:])
st.write("Depth:", depth[-5:])
st.write("Momentum:", momentum.tail())
st.write("Acceleration:", acceleration.tail())
