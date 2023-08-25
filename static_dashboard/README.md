# static dashboard

## V1 - Prototype

<p align="center">
<img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/dashboard.gif" data-canonical- width="800" height="400" align="center" />
</p>

Quick working demo that will guide further development. Main issues to fix at this stage:
 - app caches data, so on every restart it needs to download it again
 - inefficient time series caching, only able to cache entire series, doesn't use overlap between them
 - limited set of tickers and only one plot

## V2 - Efficient Backend

<p align="center">
<img src="https://github.com/msztylko/dashboard-prototyping/blob/master/images/backend.gif" data-canonical- width="800" height="400" align="center" />
</p>

### Notes to self

#### V1
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

One of the most useful changes at the early stage is `st.cache_data`. 

```python
@st.cache_data
def get_data(ticker, start_date, end_date):
    return yf.download(ticker, start_date, end_date)


data = get_data(ticker, start_date, end_date)
```

primarily to avoid redownloading data any time you click something on the dashboard. 
By default, [Streamlit](https://docs.streamlit.io/library/advanced-features/caching) runs your script from top to bottom at every user interaction or code change.

#### V2

We can cache data used by dashboard with Redis:

```python
client = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

def get_data(ticker, start_date, end_date):
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
```

But there are at least 2 issues:
 - still inefficient for time series data
 - quick and dirty solution: very simple serialization and `get_data` starts to do too much

Let's create a backend that will be responsible for getting 3rd party data and persisting it (to cache and later to DB).

Minimal backend

```python
from flask import Flask
import json
import yfinance as yf
import redis
import datetime

redis = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

app = Flask(__name__)


@app.route("/")
def index():
    return "Backend for stock prices dashboard"


@app.route("/prices/<ticker>/<start>/<end>")
def prices(ticker: str, start: str, end: str):
    start_date = datetime.datetime.fromisoformat(start)
    end_date = datetime.datetime.fromisoformat(end)
    cache_key = f"{ticker}:{start_date.timestamp()}:{end_date.timestamp()}"
    cached_raw_value = redis.get(cache_key)

    if cached_raw_value is not None:
        return json.loads(cached_raw_value)

    value = yf.download(ticker, start_date, end_date).to_json()
    raw_value = json.dumps(value)
    redis.set(cache_key, raw_value, ex=cache_ttl)
    return value


if __name__ == "__main__":
    app.run(host="0.0.0.0")
```

Adding Redis cache to backend:

```python
redis = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

def fetch_prices(
    ticker: str, start_date: datetime.datetime, end_date: datetime.datetime
) -> list[PriceData]:
    ...

def fetch_prices_with_cache(
    ticker: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
) -> list[PriceData]:
    cache_key = f"{ticker}:{start_date.timestamp()}:{end_date.timestamp()}"

    cached_raw_value = redis.get(cache_key)
    if cached_raw_value is not None:
        ta = TypeAdapter(list[PriceData])
        return ta.validate_python(json.loads(cached_raw_value))

    value = fetch_prices(ticker, start_date, end_date)
    raw_value = json.dumps(value, separators=(",", ":"), default=pydantic_encoder)
    redis.set(cache_key, raw_value, ex=cache_ttl)
    return value
```

Since we are storing time series as JSON it might be worth to try [Redis-JSON](https://redis.com/modules/redis-json/) in the future.

Main problem at this stage is inefficieny of time series caching. Let's establish simple [benchmark](https://github.com/msztylko/dashboard-prototyping/blob/master/static_dashboard/load_test.py) to compare before and after the changes:

```bash
********** LOAD TEST **********


********** SUMMARY **********
Total time elapsed: 50.33 seconds
Average time elapsed: 0.50 seconds
```
