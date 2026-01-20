import os
import sqlite3
import datetime
from typing import List, Dict, Any
from contextlib import contextmanager


class MonitorTickersRepository:
    """
    Repository for managing live market monitor tickers

    Stores the list of tickers that should be displayed in the live market monitor.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data',
                'strategy_runs.db'
            )

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and table if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitor_tickers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL UNIQUE,
                    display_order INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_monitor_tickers_order
                ON monitor_tickers(display_order)
            ''')

            conn.commit()

            # Initialize with default tickers if empty
            cursor.execute('SELECT COUNT(*) FROM monitor_tickers')
            count = cursor.fetchone()[0]

            if count == 0:
                default_tickers = ['AAPL', 'MSFT', 'GOOGL']
                for idx, ticker in enumerate(default_tickers):
                    cursor.execute('''
                        INSERT INTO monitor_tickers (ticker, display_order, created_at)
                        VALUES (?, ?, ?)
                    ''', (ticker, idx, datetime.datetime.now().isoformat()))
                conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_all_tickers(self) -> List[str]:
        """
        Get all monitor tickers ordered by display_order

        Returns:
            List of ticker symbols
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ticker
                FROM monitor_tickers
                ORDER BY display_order ASC, created_at ASC
            ''')

            rows = cursor.fetchall()
            return [row['ticker'] for row in rows]

    def get_all_tickers_detailed(self) -> List[Dict[str, Any]]:
        """
        Get all monitor tickers with full details

        Returns:
            List of ticker dicts with id, ticker, display_order, created_at
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, ticker, display_order, created_at
                FROM monitor_tickers
                ORDER BY display_order ASC, created_at ASC
            ''')

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def add_ticker(self, ticker: str) -> int:
        """
        Add a ticker to the monitor list

        Args:
            ticker: Ticker symbol (will be uppercased)

        Returns:
            ID of the created entry

        Raises:
            ValueError: If ticker already exists
        """
        ticker = ticker.upper().strip()

        if not ticker:
            raise ValueError("Ticker cannot be empty")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if ticker already exists
            cursor.execute('SELECT id FROM monitor_tickers WHERE ticker = ?', (ticker,))
            if cursor.fetchone():
                raise ValueError(f"Ticker {ticker} already exists in monitor list")

            # Get max display_order and add to end
            cursor.execute('SELECT COALESCE(MAX(display_order), -1) + 1 FROM monitor_tickers')
            next_order = cursor.fetchone()[0]

            created_at = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO monitor_tickers (ticker, display_order, created_at)
                VALUES (?, ?, ?)
            ''', (ticker, next_order, created_at))

            conn.commit()
            return cursor.lastrowid

    def remove_ticker(self, ticker: str) -> bool:
        """
        Remove a ticker from the monitor list

        Args:
            ticker: Ticker symbol to remove

        Returns:
            True if ticker was removed, False if not found
        """
        ticker = ticker.upper().strip()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM monitor_tickers WHERE ticker = ?', (ticker,))
            conn.commit()
            return cursor.rowcount > 0

    def update_order(self, ticker_order: List[str]) -> bool:
        """
        Update the display order of all tickers

        Args:
            ticker_order: List of tickers in desired display order

        Returns:
            True if successful
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for idx, ticker in enumerate(ticker_order):
                ticker = ticker.upper().strip()
                cursor.execute('''
                    UPDATE monitor_tickers
                    SET display_order = ?
                    WHERE ticker = ?
                ''', (idx, ticker))

            conn.commit()
            return True

    def clear_all(self) -> int:
        """
        Remove all tickers from monitor list

        Returns:
            Number of tickers removed
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM monitor_tickers')
            count = cursor.rowcount
            conn.commit()
            return count

    def ticker_exists(self, ticker: str) -> bool:
        """
        Check if a ticker exists in the monitor list

        Args:
            ticker: Ticker symbol to check

        Returns:
            True if ticker exists, False otherwise
        """
        ticker = ticker.upper().strip()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM monitor_tickers WHERE ticker = ? LIMIT 1', (ticker,))
            return cursor.fetchone() is not None
