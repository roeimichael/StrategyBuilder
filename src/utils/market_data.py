"""Market data utilities for stock analysis"""

import datetime as dt

import numpy as np
import pandas as pd
import pandas_datareader as pdr
import requests
from sklearn.linear_model import LinearRegression


def get_stock_table(url):
    """Fetch stock table from URL"""
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.get(url, headers=header)
    ticker_series = pd.read_html(r.text)
    return ticker_series[1]


def calculate_beta_for_stock(stock_ticker, interval="w", start=dt.datetime(2020, 1, 1), end=dt.datetime.today()):
    """Calculate beta for a stock relative to S&P 500"""
    stock_list = [stock_ticker, '^GSPC']
    data = pdr.get_data_yahoo(stock_list, start, end, interval=interval)
    data = data['Adj Close']
    log_returns = np.log(data / data.shift())
    cov = log_returns.cov()
    var = log_returns['^GSPC'].var()
    return cov.loc[stock_ticker, '^GSPC'] / var


def add_beta_to_dataframe(stock_df):
    """Add beta values to stock dataframe"""
    beta_list = []
    for stock in stock_df['Ticker symbol']:
        beta_list.append(calculate_beta_for_stock(stock))
    stock_df = stock_df.assign(Beta=beta_list)
    stock_df.to_csv('snp600SmallCapWithBeta.csv')


if __name__ == '__main__':
    ticker = 'AAPL'
    url = r"https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"
    stock_table = get_stock_table(url)
    add_beta_to_dataframe(stock_table)
