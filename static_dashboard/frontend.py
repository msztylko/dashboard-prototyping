import yfinance as yf
import requests
import pandas as pd
import json
import datetime
import streamlit as st
import plotly.graph_objects as go
import redis
import datetime

client = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

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
ticker = st.sidebar.text_input("ticker", "AAPL")
value = st.sidebar.selectbox("value to plot", AVAILABLE_VALUES)


def get_data(ticker, start_date, end_date):
    end_date = date_to_datetime(end_date).isoformat()
    start_date = date_to_datetime(start_date).isoformat()
    data = requests.get(
        f"http://localhost:5000/prices/{ticker}/{start_date}/{end_date}"
    )
    return pd.DataFrame(data.json())


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
