import requests
import time
import concurrent.futures
import pandas as pd
import yfinance as yf
import threading
import numpy as np


# def get_stock_close_by_ticker(ticker):
#     stock = yf.Ticker(ticker)
#     stock_df = stock.history(period='1y')
#     return stock_df['Close'].to_frame(name="Close")


def get_stock_list_from_csv(csv_path):
    stock_df = pd.read_csv(csv_path)
    stock_tickers_series = stock_df['Symbol']
    stock_list = stock_tickers_series.tolist()
    return stock_list


def create_threads(splits):
    lst = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        stocks = executor.map(scan_condition, splits)
        for ticker in stocks:
            if ticker is not None:
                lst.append(ticker)
        return lst


def scan_condition():
    pass


def main():
    csv_path = '...'
    list_inserted = get_stock_list_from_csv(csv_path)
    t1 = time.perf_counter()
    splits = np.array_split(list_inserted, 25)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in executor.map(create_threads, splits):
            if len(i) != 0:
                received_results = received_results + i
    t2 = time.perf_counter()
    print(f'Finished in {t2 - t1} seconds')
    print(received_results)


if __name__ == '__main__':
    main()
