import datetime
import json

import pydantic
import pytz
import redis
import yfinance as yf
from flask import Flask
from pydantic import BaseModel, ConfigDict, TypeAdapter, field_validator
from pydantic.json import pydantic_encoder

week = datetime.timedelta(days=7)

redis = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

app = Flask(__name__)


class WeeklyBucket(BaseModel):
    """Model to represent a weekly bucket, the unit of fetching data."""

    start: datetime.datetime

    @property
    def end(self) -> datetime:
        return self.start + week

    @field_validator("start")
    @classmethod
    def align_start(cls, v: datetime) -> datetime:
        """Align weekly bucket start date."""
        seconds_in_week = week.total_seconds()
        return datetime.datetime.fromtimestamp(
            (v.timestamp() // seconds_in_week * seconds_in_week), datetime.timezone.utc
        )

    def next(self) -> "WeeklyBucket":
        """Return the next bucket."""
        return WeeklyBucket(start=self.end)

    def cache_key(self) -> str:
        """Helper function to return the cache key by the bucket start date."""
        return f"{int(self.start.timestamp())}"

    model_config = ConfigDict(frozen=True)


def get_buckets(start_date: datetime, end_date: datetime) -> list[WeeklyBucket]:
    """Return the list of weekly buckets in a date range."""
    buckets: list[WeeklyBucket] = []

    if end_date < start_date:
        raise ValueError(f"{end_date=} must be greater than {start_date=}")

    bucket = WeeklyBucket(start=start_date)
    while True:
        buckets.append(bucket)
        bucket = bucket.next()
        if bucket.end >= end_date:
            break
    return buckets


class PriceData(pydantic.BaseModel):
    timestamp: datetime.datetime
    ticker: str
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float
    model_config = ConfigDict(frozen=True)


def fetch_prices(
    ticker: str, start_date: datetime.datetime, end_date: datetime.datetime
) -> list[PriceData]:
    start_date = start_date.date().isoformat()
    end_date = end_date.date().isoformat()
    data = yf.download(ticker, start_date, end_date)
    data.columns = data.columns.str.replace(r" ", "_")
    return [
        PriceData(
            timestamp=row.Index.replace(tzinfo=datetime.timezone.utc),
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
    buckets = get_buckets(start_date, end_date)

    transactions = []
    for bucket in buckets:
        cache_key = f"{ticker}:{bucket.cache_key()}"

        cached_raw_value = redis.get(cache_key)
        if cached_raw_value is not None:
            ta = TypeAdapter(list[PriceData])
            transactions += ta.validate_python(json.loads(cached_raw_value))
            continue

        value = fetch_prices(ticker, bucket.start, bucket.end)
        raw_value = json.dumps(value, separators=(",", ":"), default=pydantic_encoder)
        redis.set(cache_key, raw_value, ex=cache_ttl)
        transactions += value

    return [tx for tx in transactions if start_date <= tx.timestamp < end_date]


def get_cache_ttl(bucket: WeeklyBucket):
    if bucket.end >= datetime.now(tz=datetime.timezone.utc):
        return int(timedelta(minutes=10).total_seconds())
    return int(timedelta(days=30).total_seconds())


@app.route("/")
def index():
    return "Backend for stock prices dashboard"


@app.route("/prices/<ticker>/<start>/<end>")
def prices(ticker: str, start: str, end: str):
    start_date = datetime.datetime.fromisoformat(start).replace(tzinfo=pytz.UTC)
    end_date = datetime.datetime.fromisoformat(end).replace(tzinfo=pytz.UTC)
    prices = fetch_prices_with_cache(ticker, start_date, end_date)
    return [price.model_dump() for price in prices]


if __name__ == "__main__":
    app.run(host="0.0.0.0")
