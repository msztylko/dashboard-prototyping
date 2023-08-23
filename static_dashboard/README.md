# static dashboard

## V1 - Prototype

<p align="center">
<img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/dashboard.gif" data-canonical- width="800" height="400" align="center" />
</p>

Quick working demo that will guide further development. Main issues to fix at this stage:
 - app caches data, so on every restart it needs to download it again
 - inefficient time series caching, only able to cache entire series, doesn't use overlap between them
 - limited set of tickers and only one plot

### Notes to self

Basic structure of a Streamlit app can be very lean:

```python
import yfinance as yf
import datetime
import streamlit as st
import plotly.graph_objects as go

AVAILABLE_TICKERS = ("AAPL", "GOOGL", "AMZN")
AVAILABLE_VALUES = ("Open", "High", "Low", "Close", "Adj Close", "Volume")

st.markdown(
    "<h1 style='text-align: center; color: orange;'> Stock Prices</h1>",
    unsafe_allow_html=True,
)

start_date = st.date_input("Select start date", datetime.date(2013, 1, 1)) 
end_date = st.date_input("Select end date", datetime.date.today())
ticker = st.selectbox("ticker", AVAILABLE_TICKERS)
value = st.selectbox("value to plot", AVAILABLE_VALUES)

data = yf.download(ticker, start_date, end_date)

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
```

Here, the main focus is the app layout and plots.
