import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# ================================================
# FETCH DATA FROM BYBIT (NO BLOCKING)
# ================================================
def fetch_klines(symbol="BTCUSDT", interval="60", limit=200):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        st.error("Error fetching data from Bybit")
        return None

    raw = r.json()

    if "result" not in raw or "list" not in raw["result"]:
        st.error("Invalid data format from Bybit")
        return None

    rows = raw["result"]["list"]
    data = []

    for k in rows:
        data.append({
            "time": pd.to_datetime(int(k[0]), unit="ms"),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4])
        })

    return pd.DataFrame(data)

# ================================================
# SIMPLE SWING DETECTION
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
# STREAMLIT UI
# ================================================
st.set_page_config(page_title="YTC Price Action Dashboard", layout="wide")

st.title("📊 YTC Price Action Dashboard (Bybit Version)")
st.write("No indicators. Pure price action. No Binance blocking.")

symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT"])
interval = st.sidebar.selectbox("Interval", ["1", "3", "5", "15", "30", "60", "240", "D"])
limit = st.sidebar.slider("Candles", 100, 500, 200)

df = fetch_klines(symbol, interval, limit)

if df is None:
    st.stop()

swings = zigzag(df)

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
