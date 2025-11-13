"""
Database utilities for StrategyBuilder
Stores backtest configurations and monitoring list
"""
import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class TradingDatabase:
    """Handles all database operations for backtests and monitoring"""

    def __init__(self, db_path: str = "data/trading.db"):
        """Initialize database connection"""
        self.db_path = db_path

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for backtest configurations and results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strategy TEXT NOT NULL,
                interval TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                parameters TEXT NOT NULL,
                start_value REAL,
                end_value REAL,
                return_pct REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                total_trades INTEGER,
                win_rate REAL,
                avg_pnl REAL,
                created_at TEXT NOT NULL,
                notes TEXT
            )
        """)

        # Table for monitored stocks (active monitoring list)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strategy TEXT NOT NULL,
                interval TEXT NOT NULL,
                parameters TEXT NOT NULL,
                backtest_id INTEGER,
                status TEXT DEFAULT 'active',
                added_at TEXT NOT NULL,
                last_checked TEXT,
                FOREIGN KEY (backtest_id) REFERENCES backtests(id)
            )
        """)

        # Table for live trading signals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_date TEXT NOT NULL,
                price REAL,
                size INTEGER,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (monitor_id) REFERENCES monitored_stocks(id)
            )
        """)

        # Table for positions (open/closed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                size INTEGER NOT NULL,
                exit_date TEXT,
                exit_price REAL,
                pnl REAL,
                pnl_pct REAL,
                status TEXT DEFAULT 'open',
                created_at TEXT NOT NULL,
                FOREIGN KEY (monitor_id) REFERENCES monitored_stocks(id)
            )
        """)

        conn.commit()
        conn.close()

    def save_backtest(self, results: Dict[str, Any], strategy: str,
                     parameters: Dict[str, Any], notes: str = "") -> int:
        """
        Save backtest results to database

        Returns:
            Backtest ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate win rate and avg P&L from trades
        trades = results.get('trades', [])
        win_rate = 0.0
        avg_pnl = 0.0

        if trades:
            winning_trades = [t for t in trades if t['pnl'] > 0]
            win_rate = (len(winning_trades) / len(trades)) * 100
            avg_pnl = sum(t['pnl'] for t in trades) / len(trades)

        cursor.execute("""
            INSERT INTO backtests (
                ticker, strategy, interval, start_date, end_date, parameters,
                start_value, end_value, return_pct, sharpe_ratio, max_drawdown,
                total_trades, win_rate, avg_pnl, created_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            results['ticker'],
            strategy,
            results['interval'],
            str(results['start_date']),
            str(results['end_date']),
            json.dumps(parameters),
            results['start_value'],
            results['end_value'],
            results['return_pct'],
            results.get('sharpe_ratio'),
            results.get('max_drawdown'),
            results['total_trades'],
            win_rate,
            avg_pnl,
            datetime.datetime.now().isoformat(),
            notes
        ))

        backtest_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return backtest_id

    def get_backtests(self, limit: int = 50, ticker: str = None,
                     strategy: str = None) -> List[Dict[str, Any]]:
        """
        Get backtest history

        Args:
            limit: Maximum number of results
            ticker: Filter by ticker (optional)
            strategy: Filter by strategy (optional)

        Returns:
            List of backtest records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

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

        cursor.execute(query, params)
        rows = cursor.fetchall()

        backtests = []
        for row in rows:
            backtest = dict(row)
            backtest['parameters'] = json.loads(backtest['parameters'])
            backtests.append(backtest)

        conn.close()
        return backtests

    def add_to_monitoring(self, ticker: str, strategy: str, interval: str,
                         parameters: Dict[str, Any], backtest_id: int = None) -> int:
        """
        Add stock to monitoring list

        Returns:
            Monitor ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO monitored_stocks (
                ticker, strategy, interval, parameters, backtest_id,
                status, added_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            strategy,
            interval,
            json.dumps(parameters),
            backtest_id,
            'active',
            datetime.datetime.now().isoformat()
        ))

        monitor_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return monitor_id

    def get_monitored_stocks(self, status: str = 'active') -> List[Dict[str, Any]]:
        """Get list of monitored stocks"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM monitored_stocks
            WHERE status = ?
            ORDER BY added_at DESC
        """, (status,))

        rows = cursor.fetchall()

        monitored = []
        for row in rows:
            stock = dict(row)
            stock['parameters'] = json.loads(stock['parameters'])
            monitored.append(stock)

        conn.close()
        return monitored

    def remove_from_monitoring(self, monitor_id: int):
        """Remove stock from monitoring (set to inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE monitored_stocks
            SET status = 'inactive'
            WHERE id = ?
        """, (monitor_id,))

        conn.commit()
        conn.close()

    def log_signal(self, monitor_id: int, ticker: str, signal_type: str,
                   price: float, size: int = None, reason: str = ""):
        """Log a trading signal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trading_signals (
                monitor_id, ticker, signal_type, signal_date, price, size, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            monitor_id,
            ticker,
            signal_type,
            datetime.date.today().isoformat(),
            price,
            size,
            reason,
            datetime.datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_signals(self, monitor_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent trading signals"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

        if monitor_id:
            cursor.execute("""
                SELECT * FROM trading_signals
                WHERE monitor_id = ? AND signal_date >= ?
                ORDER BY created_at DESC
            """, (monitor_id, cutoff_date))
        else:
            cursor.execute("""
                SELECT * FROM trading_signals
                WHERE signal_date >= ?
                ORDER BY created_at DESC
            """, (cutoff_date,))

        rows = cursor.fetchall()
        signals = [dict(row) for row in rows]

        conn.close()
        return signals

    def update_monitor_last_checked(self, monitor_id: int):
        """Update last checked timestamp for monitored stock"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE monitored_stocks
            SET last_checked = ?
            WHERE id = ?
        """, (datetime.datetime.now().isoformat(), monitor_id))

        conn.commit()
        conn.close()
