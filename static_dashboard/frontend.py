import yfinance as yf
import pandas as pd
import json
import datetime
import streamlit as st
import plotly.graph_objects as go
import redis
import datetime

client = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

AVAILABLE_TICKERS = ("AAPL", "GOOGL", "AMZN")
AVAILABLE_VALUES = ("Open", "High", "Low", "Close", "Adj Close", "Volume")

st.markdown(
    "<h1 style='text-align: center; color: orange;'> Stock Prices</h1>",
    unsafe_allow_html=True,
)


def date_to_datetime(dt):
    return datetime.datetime.combine(dt, datetime.datetime.min.time())


start_date = st.sidebar.date_input(
    "Select start date", datetime.datetime(2013, 1, 1, 0, 0)
)
end_date = st.sidebar.date_input("Select end date", datetime.date.today())
ticker = st.sidebar.selectbox("ticker", AVAILABLE_TICKERS)
value = st.sidebar.selectbox("value to plot", AVAILABLE_VALUES)


def get_data(ticker, start_date, end_date):
    # FIXME
    end_date = date_to_datetime(end_date)
    start_date = date_to_datetime(start_date)
    cache_key = f"{ticker}:{start_date.timestamp()}:{end_date.timestamp()}"
    cached_raw_value = client.get(cache_key)

    if cached_raw_value is not None:
        return pd.read_json(json.loads(cached_raw_value))

    value = yf.download(ticker, start_date, end_date)
    raw_value = json.dumps(value.to_json())
    client.set(cache_key, raw_value, ex=cache_ttl)
    return value


data = get_data(ticker, start_date, end_date)

fig = go.Figure()
fig.add_scatter(x=data.index, y=data[value], name=value)
fig.update_layout(
    title_text=f"{ticker} {value}",
    title_x=0.5,
    xaxis_title="Date",
    yaxis_title=value,
    legend_title=ticker,
)

st.plotly_chart(fig)
