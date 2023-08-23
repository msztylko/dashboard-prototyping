from flask import Flask
import json
import yfinance as yf
import redis
import datetime
    
redis = redis.Redis()
cache_ttl = int(datetime.timedelta(hours=3).total_seconds())

app = Flask(__name__)

@app.route('/')
def index():
    return 'Backend for stock prices dashboard'

@app.route('/prices/<ticker>/<start>/<end>')
def prices(ticker: str, start: str, end: str):
    start_date = datetime.datetime.fromisoformat(start)
    end_date = datetime.datetime.fromisoformat(end)
    cache_key = f"{ticker}:{start_date.timestamp()}:{end_date.timestamp()}"
    cached_raw_value = redis.get(cache_key)
    
    if cached_raw_value is not None:
        return json.loads(cached_raw_value)

    value = yf.download(ticker, start_date, end_date)
    raw_value = json.dumps(value.to_json())
    redis.set(cache_key, raw_value, ex=cache_ttl)
    return value
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')
