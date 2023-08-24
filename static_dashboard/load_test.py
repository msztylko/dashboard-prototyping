import datetime
import random
import time
from functools import partial

import requests

BACKEND_URL = "http://localhost:5000"


def gen_random_date():
    rand_year = partial(random.choice, range(2010, 2023))
    rand_month = partial(random.choice, range(1, 13))
    rand_day = partial(random.choice, range(1, 28))

    return datetime.datetime(rand_year(), rand_month(), rand_day(), 0, 0)


def test_backend(ticker, start_date, end_date):
    data = requests.get(f"{BACKEND_URL}/prices/{ticker}/{start_date}/{end_date}")
    return data


if __name__ == "__main__":
    num_tests = 100
    ticker = "AAPL"
    times = []

    print("*" * 10 + " LOAD TEST " + "*" * 10)
    print(f"Testing {num_tests} requests.")
    print()

    while num_tests > 0:
        start_date = gen_random_date()
        end_date = start_date + datetime.timedelta(days=365)
        # print(f"Requesting {ticker=}, {start_date=}, {end_date=}")
        start = time.time()
        test_backend(ticker, start_date, end_date)
        end = time.time()
        elapsed = end - start
        # print(f"Request took {elapsed:.2f} seconds.")
        times.append(elapsed)
        num_tests -= 1

    print()
    print("*" * 10 + " SUMMARY " + "*" * 10)
    print(f"Total time elapsed: {sum(times):.2f} seconds")
    print(f"Average time elapsed: {sum(times)/len(times):.2f} seconds")
