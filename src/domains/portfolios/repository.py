import os
import sqlite3
import datetime
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class PortfolioRepository:
    """Repository for persisting portfolios."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data',
                'portfolios.db'
            )

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    holdings_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> int:
        """Create a new portfolio and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO portfolios (name, description, holdings_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                portfolio_data['name'],
                portfolio_data.get('description'),
                json.dumps([h.dict() for h in portfolio_data['holdings']]),
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def get_portfolio_by_id(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a portfolio by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM portfolios WHERE id = ?', (portfolio_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def list_portfolios(self) -> List[Dict[str, Any]]:
        """List all portfolios."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM portfolios ORDER BY updated_at DESC')
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update_portfolio(self, portfolio_id: int, updates: Dict[str, Any]) -> bool:
        """Update a portfolio. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            values = []

            if 'name' in updates:
                set_clauses.append('name = ?')
                values.append(updates['name'])
            if 'description' in updates:
                set_clauses.append('description = ?')
                values.append(updates['description'])
            if 'holdings' in updates:
                set_clauses.append('holdings_json = ?')
                values.append(json.dumps([h.dict() for h in updates['holdings']]))

            if not set_clauses:
                return False

            set_clauses.append('updated_at = ?')
            values.append(datetime.datetime.now().isoformat())
            values.append(portfolio_id)

            query = f"UPDATE portfolios SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0

    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolios WHERE id = ?', (portfolio_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        holdings = json.loads(row['holdings_json'])
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'holdings': holdings,
            'total_stocks': len(holdings),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
