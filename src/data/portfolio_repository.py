import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from pathlib import Path
from src.config.constants import DB_PATH


class PortfolioRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    position_size REAL NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_portfolio_ticker
                ON portfolio_positions(ticker)
            ''')
            conn.commit()

    def add_position(self, position: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO portfolio_positions (
                    ticker, quantity, entry_price, entry_date, position_size, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position['ticker'],
                position['quantity'],
                position['entry_price'],
                position['entry_date'],
                position['position_size'],
                position.get('notes'),
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_positions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, ticker, quantity, entry_price, entry_date, position_size,
                       notes, created_at, updated_at
                FROM portfolio_positions
                ORDER BY entry_date DESC
            ''')
            rows = cursor.fetchall()

            positions = []
            for row in rows:
                positions.append({
                    'id': row['id'],
                    'ticker': row['ticker'],
                    'quantity': row['quantity'],
                    'entry_price': row['entry_price'],
                    'entry_date': row['entry_date'],
                    'position_size': row['position_size'],
                    'notes': row['notes'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return positions

    def get_position_by_id(self, position_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, ticker, quantity, entry_price, entry_date, position_size,
                       notes, created_at, updated_at
                FROM portfolio_positions
                WHERE id = ?
            ''', (position_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return {
                'id': row['id'],
                'ticker': row['ticker'],
                'quantity': row['quantity'],
                'entry_price': row['entry_price'],
                'entry_date': row['entry_date'],
                'position_size': row['position_size'],
                'notes': row['notes'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

    def update_position(self, position_id: int, updates: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()

            fields = []
            values = []

            allowed_fields = ['ticker', 'quantity', 'entry_price', 'entry_date', 'position_size', 'notes']
            for field in allowed_fields:
                if field in updates:
                    fields.append(f"{field} = ?")
                    values.append(updates[field])

            if not fields:
                return False

            fields.append("updated_at = ?")
            values.append(now)
            values.append(position_id)

            query = f"UPDATE portfolio_positions SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0

    def delete_position(self, position_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolio_positions WHERE id = ?', (position_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_total_portfolio_value(self) -> float:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(position_size) as total FROM portfolio_positions')
            row = cursor.fetchone()
            return row['total'] if row['total'] else 0.0

    def clear_all_positions(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolio_positions')
            conn.commit()
            return cursor.rowcount
