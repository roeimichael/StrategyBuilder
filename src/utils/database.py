"""Database utilities for StrategyBuilder"""

import datetime
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional


class TradingDatabase:
    """Handles all database operations for backtests and monitoring"""

    SCHEMA = {
        'backtests': """CREATE TABLE IF NOT EXISTS backtests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL, strategy TEXT NOT NULL, interval TEXT NOT NULL,
            start_date TEXT NOT NULL, end_date TEXT NOT NULL, parameters TEXT NOT NULL,
            start_value REAL, end_value REAL, return_pct REAL, sharpe_ratio REAL,
            max_drawdown REAL, total_trades INTEGER, win_rate REAL, avg_pnl REAL,
            created_at TEXT NOT NULL, notes TEXT
        )""",
        'monitored_stocks': """CREATE TABLE IF NOT EXISTS monitored_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL, strategy TEXT NOT NULL, interval TEXT NOT NULL,
            parameters TEXT NOT NULL, backtest_id INTEGER, status TEXT DEFAULT 'active',
            added_at TEXT NOT NULL, last_checked TEXT,
            FOREIGN KEY (backtest_id) REFERENCES backtests(id)
        )""",
        'trading_signals': """CREATE TABLE IF NOT EXISTS trading_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER NOT NULL, ticker TEXT NOT NULL, signal_type TEXT NOT NULL,
            signal_date TEXT NOT NULL, price REAL, size INTEGER, reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (monitor_id) REFERENCES monitored_stocks(id)
        )""",
        'positions': """CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER NOT NULL, ticker TEXT NOT NULL,
            entry_date TEXT NOT NULL, entry_price REAL NOT NULL, size INTEGER NOT NULL,
            exit_date TEXT, exit_price REAL, pnl REAL, pnl_pct REAL,
            status TEXT DEFAULT 'open', created_at TEXT NOT NULL,
            FOREIGN KEY (monitor_id) REFERENCES monitored_stocks(id)
        )"""
    }

    def __init__(self, db_path: str = "data/trading.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def _get_connection(self, row_factory=False):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        if row_factory:
            conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_database(self):
        """Create tables if they don't exist"""
        with self._get_connection() as conn:
            for table_sql in self.SCHEMA.values():
                conn.execute(table_sql)

    def save_backtest(self, results: Dict[str, Any], strategy: str,
                     parameters: Dict[str, Any], notes: str = "") -> int:
        """Save backtest results to database"""
        trades = results.get('trades', [])
        win_rate = avg_pnl = 0.0
        if trades:
            win_rate = (len([t for t in trades if t['pnl'] > 0]) / len(trades)) * 100
            avg_pnl = sum(t['pnl'] for t in trades) / len(trades)

        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO backtests (ticker, strategy, interval, start_date, end_date, parameters,
                    start_value, end_value, return_pct, sharpe_ratio, max_drawdown,
                    total_trades, win_rate, avg_pnl, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (results['ticker'], strategy, results['interval'], str(results['start_date']),
                  str(results['end_date']), json.dumps(parameters), results['start_value'],
                  results['end_value'], results['return_pct'], results.get('sharpe_ratio'),
                  results.get('max_drawdown'), results['total_trades'], win_rate, avg_pnl,
                  datetime.datetime.now().isoformat(), notes))
            return cursor.lastrowid

    def get_backtests(self, limit: int = 50, ticker: str = None,
                     strategy: str = None) -> List[Dict[str, Any]]:
        """Get backtest history with optional filters"""
        query = "SELECT * FROM backtests WHERE 1=1"
        params = []

        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection(row_factory=True) as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row, parameters=json.loads(row['parameters'])) for row in rows]

    def add_to_monitoring(self, ticker: str, strategy: str, interval: str,
                         parameters: Dict[str, Any], backtest_id: int = None) -> int:
        """Add stock to monitoring list"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO monitored_stocks (ticker, strategy, interval, parameters, backtest_id, status, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ticker, strategy, interval, json.dumps(parameters), backtest_id, 'active',
                  datetime.datetime.now().isoformat()))
            return cursor.lastrowid

    def get_monitored_stocks(self, status: str = 'active') -> List[Dict[str, Any]]:
        """Get list of monitored stocks"""
        with self._get_connection(row_factory=True) as conn:
            rows = conn.execute("""
                SELECT * FROM monitored_stocks WHERE status = ? ORDER BY added_at DESC
            """, (status,)).fetchall()
            return [dict(row, parameters=json.loads(row['parameters'])) for row in rows]

    def remove_from_monitoring(self, monitor_id: int):
        """Remove stock from monitoring (set to inactive)"""
        with self._get_connection() as conn:
            conn.execute("UPDATE monitored_stocks SET status = 'inactive' WHERE id = ?", (monitor_id,))

    def log_signal(self, monitor_id: int, ticker: str, signal_type: str,
                   price: float, size: int = None, reason: str = ""):
        """Log a trading signal"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO trading_signals (monitor_id, ticker, signal_type, signal_date, price, size, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (monitor_id, ticker, signal_type, datetime.date.today().isoformat(),
                  price, size, reason, datetime.datetime.now().isoformat()))

    def get_signals(self, monitor_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent trading signals"""
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

        with self._get_connection(row_factory=True) as conn:
            if monitor_id:
                rows = conn.execute("""
                    SELECT * FROM trading_signals WHERE monitor_id = ? AND signal_date >= ?
                    ORDER BY created_at DESC
                """, (monitor_id, cutoff_date)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM trading_signals WHERE signal_date >= ?
                    ORDER BY created_at DESC
                """, (cutoff_date,)).fetchall()
            return [dict(row) for row in rows]

    def update_monitor_last_checked(self, monitor_id: int):
        """Update last checked timestamp for monitored stock"""
        with self._get_connection() as conn:
            conn.execute("UPDATE monitored_stocks SET last_checked = ? WHERE id = ?",
                        (datetime.datetime.now().isoformat(), monitor_id))
