import os
import sqlite3
import datetime
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

class RunRepository:
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
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    cash REAL NOT NULL,
                    pnl REAL,
                    return_pct REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    created_at TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ticker ON strategy_runs(ticker)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_strategy ON strategy_runs(strategy)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at ON strategy_runs(created_at DESC)
            ''')
            conn.commit()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save_run(self, run_record: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            parameters_json = json.dumps(run_record.get('parameters', {}))
            created_at = datetime.datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO strategy_runs (
                    ticker, strategy, parameters_json, start_date, end_date, interval, cash,
                    pnl, return_pct, sharpe_ratio, max_drawdown, total_trades,
                    winning_trades, losing_trades, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_record['ticker'],
                run_record['strategy'],
                parameters_json,
                run_record['start_date'],
                run_record['end_date'],
                run_record['interval'],
                run_record['cash'],
                run_record.get('pnl'),
                run_record.get('return_pct'),
                run_record.get('sharpe_ratio'),
                run_record.get('max_drawdown'),
                run_record.get('total_trades'),
                run_record.get('winning_trades'),
                run_record.get('losing_trades'),
                created_at
            ))
            conn.commit()
            return cursor.lastrowid

    def get_run_by_id(self, run_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM strategy_runs WHERE id = ?', (run_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(row)

    def list_runs(self, ticker: Optional[str] = None, strategy: Optional[str] = None,
                  limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM strategy_runs WHERE 1=1'
            params = []
            if ticker:
                query += ' AND ticker = ?'
                params.append(ticker)
            if strategy:
                query += ' AND strategy = ?'
                params.append(strategy)
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        result = dict(row)
        result['parameters'] = json.loads(result['parameters_json'])
        del result['parameters_json']
        return result

    def get_run_count(self, ticker: Optional[str] = None, strategy: Optional[str] = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT COUNT(*) FROM strategy_runs WHERE 1=1'
            params = []
            if ticker:
                query += ' AND ticker = ?'
                params.append(ticker)
            if strategy:
                query += ' AND strategy = ?'
                params.append(strategy)
            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def delete_run(self, run_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM strategy_runs WHERE id = ?', (run_id,))
            conn.commit()
            return cursor.rowcount > 0
