from flask import Flask
from pydantic import BaseModel
from pydantic import TypeAdapter
import pydantic
from pydantic.json import pydantic_encoder

import pydantic
import json
import yfinance as yf
import redis
import datetime

redis = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

app = Flask(__name__)


class PriceData(pydantic.BaseModel):
    timestamp: datetime.datetime
    ticker: str
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float

    class Config:
        frozen = True


def fetch_prices(
    ticker: str, start_date: datetime.datetime, end_date: datetime.datetime
) -> list[PriceData]:
    start_date = start_date.date().isoformat()
    end_date = end_date.date().isoformat()
    data = yf.download(ticker, start_date, end_date)
    data.columns = data.columns.str.replace(r" ", "_")
    return [
        PriceData(
            timestamp=row.Index.isoformat(),
            ticker=ticker,
            open=row.Open,
            high=row.High,
            low=row.Low,
            close=row.Close,
            adj_close=row.Adj_Close,
            volume=row.Volume,
        )
        for row in data.itertuples()
    ]


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
        # return pydantic.parse_raw_as(list[PriceData], cached_raw_value)

    value = fetch_prices(ticker, start_date, end_date)
    raw_value = json.dumps(value, separators=(",", ":"), default=pydantic_encoder)
    redis.set(cache_key, raw_value, ex=cache_ttl)
    return value


@app.route("/")
def index():
    return "Backend for stock prices dashboard"


@app.route("/prices/<ticker>/<start>/<end>")
def prices(ticker: str, start: str, end: str):
    start_date = datetime.datetime.fromisoformat(start)
    end_date = datetime.datetime.fromisoformat(end)
    prices = fetch_prices_with_cache(ticker, start_date, end_date)
    return [price.model_dump() for price in prices]


if __name__ == "__main__":
    app.run(host="0.0.0.0")
