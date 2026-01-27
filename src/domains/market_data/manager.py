import os
import sqlite3
import datetime
import logging
import pandas as pd
import yfinance as yf
from typing import Optional, List, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DataManager:

    def __init__(self, db_path: str = None, update_schedule: str = 'daily'):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data',
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

        # Try to get cached data
        cached_data = self._get_cached_data(ticker, start_date, end_date, interval)

        if cached_data is not None and not cached_data.empty:
            # Check if cache is complete
            if self._is_cache_complete(cached_data, start_date, end_date):
                logger.info(f"Cache hit for {ticker} ({interval}): {start_date} to {end_date}")
                return cached_data

            # Cache exists but incomplete - fetch only missing data
            logger.info(f"Partial cache for {ticker} ({interval}): fetching missing data")
            return self._smart_fetch_and_merge(ticker, start_date, end_date, interval, cached_data)

        # No cached data - fetch everything
        logger.info(f"Cache miss for {ticker} ({interval}): fetching all data")
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

    def _smart_fetch_and_merge(self, ticker: str, start_date: datetime.date,
                               end_date: datetime.date, interval: str,
                               cached_data: pd.DataFrame) -> pd.DataFrame:
        """
        Intelligently fetch only missing data ranges and merge with cached data.
        If we have 3 months cached and need 1 year, only fetch the missing 9 months.
        """
        cache_start = cached_data.index.min().date()
        cache_end = cached_data.index.max().date()

        missing_ranges = []

        # Check if we need data before cached range
        if start_date < cache_start:
            missing_ranges.append((start_date, cache_start - datetime.timedelta(days=1)))
            logger.info(f"Missing data before cache: {start_date} to {cache_start - datetime.timedelta(days=1)}")

        # Check if we need data after cached range
        if end_date > cache_end:
            missing_ranges.append((cache_end + datetime.timedelta(days=1), end_date))
            logger.info(f"Missing data after cache: {cache_end + datetime.timedelta(days=1)} to {end_date}")

        # Fetch missing data
        new_data_frames = [cached_data]
        for missing_start, missing_end in missing_ranges:
            try:
                logger.info(f"Fetching missing range for {ticker}: {missing_start} to {missing_end}")
                missing_data = self._fetch_and_cache_data(ticker, missing_start, missing_end, interval)
                if not missing_data.empty:
                    new_data_frames.append(missing_data)
            except Exception as e:
                logger.warning(f"Failed to fetch missing data for {ticker} ({missing_start} to {missing_end}): {e}")

        # Merge all data and remove duplicates
        if len(new_data_frames) > 1:
            merged_data = pd.concat(new_data_frames)
            # Remove duplicates, keeping the most recent data
            merged_data = merged_data[~merged_data.index.duplicated(keep='last')]
            merged_data = merged_data.sort_index()

            # Filter to requested range
            merged_data = merged_data[(merged_data.index.date >= start_date) &
                                     (merged_data.index.date <= end_date)]

            logger.info(f"Merged data for {ticker}: {len(merged_data)} rows covering {merged_data.index.min().date()} to {merged_data.index.max().date()}")
            return merged_data

        return cached_data

    def _clean_and_validate_data(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        df = df.dropna()

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

    def get_ticker_cache_info(self, ticker: str) -> dict:
        """
        Get cache information for a specific ticker across all intervals.
        Useful for understanding what data is already cached.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT interval, start_date, end_date, last_update
                FROM data_metadata
                WHERE ticker = ?
                ORDER BY interval
            ''', (ticker,))

            metadata = cursor.fetchall()

            if not metadata:
                return {'ticker': ticker, 'cached': False, 'intervals': []}

            intervals_info = []
            for interval, start_date, end_date, last_update in metadata:
                cursor.execute('''
                    SELECT COUNT(*) FROM ohlcv_data
                    WHERE ticker = ? AND interval = ?
                ''', (ticker, interval))
                row_count = cursor.fetchone()[0]

                intervals_info.append({
                    'interval': interval,
                    'start_date': start_date,
                    'end_date': end_date,
                    'last_update': last_update,
                    'rows': row_count
                })

            return {
                'ticker': ticker,
                'cached': True,
                'intervals': intervals_info
            }

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
    def _read_tickers_from_file() -> List[str]:
        """Read S&P 500 tickers from src/data/tickers.txt file as fallback."""
        # Get src directory (3 levels up from this file: manager.py -> market_data -> domains -> src)
        market_data_dir = os.path.dirname(__file__)
        domains_dir = os.path.dirname(market_data_dir)
        src_dir = os.path.dirname(domains_dir)
        ticker_file_path = os.path.join(src_dir, 'data', 'tickers.txt')
        try:
            with open(ticker_file_path, 'r') as f:
                tickers = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(tickers)} tickers from {ticker_file_path}")
            return tickers
        except FileNotFoundError:
            logger.error(f"Ticker file not found at {ticker_file_path}. Please create src/data/tickers.txt with S&P 500 ticker symbols.")
            raise ValueError(f"Ticker file not found at {ticker_file_path}. Cannot proceed without ticker list.")
        except Exception as e:
            logger.error(f"Failed to read tickers from file: {e}")
            raise ValueError(f"Failed to read ticker file: {str(e)}")

    @staticmethod
    def get_sp500_tickers() -> List[str]:
        """
        Get S&P 500 ticker list.
        First tries to fetch from Wikipedia with custom headers, falls back to reading from src/data/tickers.txt file.
        """
        try:
            # Use custom headers to avoid HTTP 403 errors
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            storage_options = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            table = pd.read_html(url, storage_options=storage_options)
            df = table[0]
            tickers = df['Symbol'].str.replace('.', '-').tolist()
            logger.info(f"Successfully fetched {len(tickers)} S&P 500 tickers from Wikipedia")
            return tickers
        except ImportError as e:
            logger.warning(f"Failed to fetch S&P 500 list from Wikipedia (missing dependency): {e}. Reading from file.")
            return DataManager._read_tickers_from_file()
        except Exception as e:
            logger.warning(f"Failed to fetch S&P 500 list from Wikipedia: {e}. Reading from file.")
            return DataManager._read_tickers_from_file()
