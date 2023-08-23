# static dashboard

## V1 - Prototype

<p align="center">
<img src="https://github.com/msztylko/flask-rest-api/blob/master/images/flask-rest-api.gif" data-canonical- width="800" height="400" align="center" />
</p>

Quick working demo that will guide further development. Main issues to fix at this stage:
 - app caches data, so on every restart it needs to download it again
 - inefficient time series caching, only able to cache entire series, doesn't use overlap between them
 - limited set of tickers and only one plot
