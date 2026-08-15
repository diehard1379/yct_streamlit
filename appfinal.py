import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

RELAY_URL = "https://gold-api-relay.onrender.com"  # لینک Render خودت رو اینجا بذار

def fetch_gold(interval="1m", limit=500):
    url = f"{RELAY_URL}/gold?interval={interval}"

    r = requests.get(url)

    if r.status_code != 200:
        st.error("Error fetching gold data (Relay Server)")
        return None

    raw = r.json()

    # نسخه جدید سرور: ساختار ساده و بدون chart/result
    try:
        df = pd.DataFrame({
            "time": pd.to_datetime(raw["timestamp"], unit="s"),
            "open": raw["open"],
            "high": raw["high"],
            "low": raw["low"],
            "close": raw["close"]
        })
    except:
        st.error("Invalid data format from Relay Server")
        return None

    df = df.dropna().tail(limit)
    return df

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

st.set_page_config(page_title="Gold Price Action (YTC)", layout="wide")

st.title("📊 YTC Price Action Dashboard — Gold (XAUUSD)")
st.write("دیتا از Relay Server روی Render، بدون بلاک شدن.")

tf_map = {
    "1 دقیقه": "1m",
    "5 دقیقه": "5m",
    "30 دقیقه": "30m"
}

tf = st.sidebar.selectbox("تایم‌فریم", ["1 دقیقه", "5 دقیقه", "30 دقیقه"])
limit = st.sidebar.slider("تعداد کندل", 100, 500, 300)

df = fetch_gold(tf_map[tf], limit)

if df is None:
    st.stop()

swings = zigzag(df)

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
