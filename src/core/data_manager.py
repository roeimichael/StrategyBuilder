import os
import sqlite3
import datetime
import pandas as pd
import yfinance as yf
from typing import Optional, List, Tuple
from contextlib import contextmanager


class DataManager:

    def __init__(self, db_path: str = None, update_schedule: str = 'daily'):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data',
                                   'market_data.db')

        self.db_path = db_path
        self.update_schedule = update_schedule
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ohlcv_data (
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    interval TEXT NOT NULL,
                    PRIMARY KEY (ticker, date, interval)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_metadata (
                    ticker TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    last_update TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    PRIMARY KEY (ticker, interval)
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ticker_date
                ON ohlcv_data(ticker, date, interval)
            ''')

            conn.commit()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def get_data(self, ticker: str, start_date: datetime.date, end_date: datetime.date = None,
                 interval: str = '1d', force_update: bool = False) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.date.today()

        if force_update:
            return self._fetch_and_cache_data(ticker, start_date, end_date, interval)

        cached_data = self._get_cached_data(ticker, start_date, end_date, interval)

        if cached_data is not None and not cached_data.empty:
            if self._is_cache_complete(cached_data, start_date, end_date):
                return cached_data

        return self._fetch_and_cache_data(ticker, start_date, end_date, interval)

    def _get_cached_data(self, ticker: str, start_date: datetime.date,
                         end_date: datetime.date, interval: str) -> Optional[pd.DataFrame]:
        with self._get_connection() as conn:
            query = '''
                SELECT date, open, high, low, close, volume
                FROM ohlcv_data
                WHERE ticker = ? AND interval = ?
                AND date >= ? AND date <= ?
                ORDER BY date
            '''

            df = pd.read_sql_query(
                query,
                conn,
                params=(ticker, interval, start_date.isoformat(), end_date.isoformat())
            )

            if df.empty:
                return None

            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            return df

    def _is_cache_complete(self, cached_data: pd.DataFrame,
                           start_date: datetime.date, end_date: datetime.date) -> bool:
        if cached_data.empty:
            return False

        cache_start = cached_data.index.min().date()
        cache_end = cached_data.index.max().date()

        return cache_start <= start_date and cache_end >= end_date

    def _fetch_and_cache_data(self, ticker: str, start_date: datetime.date,
                              end_date: datetime.date, interval: str) -> pd.DataFrame:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            raise ValueError(f"No data available for {ticker}")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        cleaned_data = self._clean_and_validate_data(data)

        self._cache_data(ticker, cleaned_data, interval)

        return cleaned_data

    def _clean_and_validate_data(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        df = df.dropna()

        # Remove duplicate index entries (keep first occurrence)
        # This prevents "cannot reindex on an axis with duplicate labels" error
        if not df.index.is_unique:
            df = df[~df.index.duplicated(keep='first')]

        if 'Open' in df.columns:
            df = df[(df['Open'] > 0) & (df['High'] > 0) & (df['Low'] > 0) & (df['Close'] > 0)]

        if 'High' in df.columns and 'Low' in df.columns:
            df = df[df['High'] >= df['Low']]

        if 'Open' in df.columns and 'High' in df.columns and 'Low' in df.columns and 'Close' in df.columns:
            df = df[
                (df['High'] >= df['Open']) &
                (df['High'] >= df['Close']) &
                (df['Low'] <= df['Open']) &
                (df['Low'] <= df['Close'])
                ]

        if 'Volume' in df.columns:
            df = df[df['Volume'] >= 0]

        return df

    def _cache_data(self, ticker: str, data: pd.DataFrame, interval: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for date, row in data.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO ohlcv_data
                    (ticker, date, open, high, low, close, volume, interval)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    date.strftime('%Y-%m-%d'),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume']),
                    interval
                ))

            cursor.execute('''
                INSERT OR REPLACE INTO data_metadata
                (ticker, interval, last_update, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ticker,
                interval,
                datetime.datetime.now().isoformat(),
                data.index.min().strftime('%Y-%m-%d'),
                data.index.max().strftime('%Y-%m-%d')
            ))

            conn.commit()

    def bulk_download(self, tickers: List[str], start_date: datetime.date,
                      end_date: datetime.date = None, interval: str = '1d') -> dict:
        if end_date is None:
            end_date = datetime.date.today()

        results = {}

        for ticker in tickers:
            try:
                data = self.get_data(ticker, start_date, end_date, interval)
                results[ticker] = {'success': True, 'rows': len(data)}
            except Exception as e:
                results[ticker] = {'success': False, 'error': str(e)}

        return results

    def get_cache_stats(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(DISTINCT ticker) FROM ohlcv_data')
            ticker_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM ohlcv_data')
            row_count = cursor.fetchone()[0]

            cursor.execute('SELECT ticker, interval, last_update FROM data_metadata ORDER BY last_update DESC LIMIT 10')
            recent_updates = cursor.fetchall()

            return {
                'total_tickers': ticker_count,
                'total_rows': row_count,
                'recent_updates': recent_updates,
                'db_path': self.db_path,
                'db_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            }

    def clear_cache(self, ticker: str = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if ticker:
                cursor.execute('DELETE FROM ohlcv_data WHERE ticker = ?', (ticker,))
                cursor.execute('DELETE FROM data_metadata WHERE ticker = ?', (ticker,))
            else:
                cursor.execute('DELETE FROM ohlcv_data')
                cursor.execute('DELETE FROM data_metadata')

            conn.commit()

    @staticmethod
    def get_sp500_tickers() -> List[str]:
        try:
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            return df['Symbol'].str.replace('.', '-').tolist()
        except Exception:
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
                'V', 'WMT', 'XOM', 'JPM', 'PG', 'MA', 'CVX', 'HD', 'LLY', 'ABBV',
                'MRK', 'AVGO', 'KO', 'PEP', 'COST', 'TMO', 'MCD', 'CSCO', 'ACN', 'ABT'
            ]
