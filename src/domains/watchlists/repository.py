import os
import sqlite3
import datetime
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class WatchlistRepository:
    """Repository for persisting watchlists and their positions."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data',
                'watchlists.db'
            )

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Watchlists table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    ticker TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    cash REAL NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    current_value REAL,
                    pnl REAL,
                    return_pct REAL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')

            # Positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watchlist_id INTEGER NOT NULL,
                    position_type TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    size REAL NOT NULL,
                    exit_date TEXT,
                    exit_price REAL,
                    pnl REAL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_ticker ON watchlists(ticker)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_active ON watchlists(active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_position_watchlist ON watchlist_positions(watchlist_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_position_status ON watchlist_positions(status)')

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

    def create_watchlist(self, watchlist_data: Dict[str, Any]) -> int:
        """Create a new watchlist and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO watchlists
                (name, description, ticker, strategy, parameters_json, interval, cash, active, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                watchlist_data['name'],
                watchlist_data.get('description'),
                watchlist_data['ticker'],
                watchlist_data['strategy'],
                json.dumps(watchlist_data['parameters']),
                watchlist_data['interval'],
                watchlist_data['cash'],
                1 if watchlist_data.get('active', True) else 0,
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def get_watchlist_by_id(self, watchlist_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a watchlist by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM watchlists WHERE id = ?', (watchlist_id,))
            row = cursor.fetchone()

            if row:
                return self._watchlist_row_to_dict(row)
            return None

    def list_watchlists(self, active_only: bool = False, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all watchlists with optional filters."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM watchlists WHERE 1=1'
            params = []

            if active_only:
                query += ' AND active = 1'
            if ticker:
                query += ' AND ticker = ?'
                params.append(ticker)

            query += ' ORDER BY last_updated DESC'

            cursor.execute(query, params)
            return [self._watchlist_row_to_dict(row) for row in cursor.fetchall()]

    def update_watchlist(self, watchlist_id: int, updates: Dict[str, Any]) -> bool:
        """Update a watchlist. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            values = []

            for key in ['name', 'description', 'active', 'current_value', 'pnl', 'return_pct']:
                if key in updates:
                    if key == 'active':
                        set_clauses.append('active = ?')
                        values.append(1 if updates[key] else 0)
                    else:
                        set_clauses.append(f'{key} = ?')
                        values.append(updates[key])

            if not set_clauses:
                return False

            set_clauses.append('last_updated = ?')
            values.append(datetime.datetime.now().isoformat())
            values.append(watchlist_id)

            query = f"UPDATE watchlists SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0

    def delete_watchlist(self, watchlist_id: int) -> bool:
        """Delete a watchlist and all its positions. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM watchlists WHERE id = ?', (watchlist_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Position methods
    def create_position(self, position_data: Dict[str, Any]) -> int:
        """Create a new position and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO watchlist_positions
                (watchlist_id, position_type, entry_date, entry_price, size, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                position_data['watchlist_id'],
                position_data['position_type'],
                position_data['entry_date'],
                position_data['entry_price'],
                position_data['size'],
                'OPEN'
            ))
            conn.commit()
            return cursor.lastrowid

    def close_position(self, position_id: int, exit_date: str, exit_price: float, pnl: float) -> bool:
        """Close a position. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE watchlist_positions
                SET exit_date = ?, exit_price = ?, pnl = ?, status = 'CLOSED'
                WHERE id = ?
            ''', (exit_date, exit_price, pnl, position_id))
            conn.commit()

            return cursor.rowcount > 0

    def get_positions_for_watchlist(self, watchlist_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all positions for a watchlist, optionally filtered by status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    'SELECT * FROM watchlist_positions WHERE watchlist_id = ? AND status = ? ORDER BY entry_date DESC',
                    (watchlist_id, status)
                )
            else:
                cursor.execute(
                    'SELECT * FROM watchlist_positions WHERE watchlist_id = ? ORDER BY entry_date DESC',
                    (watchlist_id,)
                )

            return [self._position_row_to_dict(row) for row in cursor.fetchall()]

    def _watchlist_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert watchlist database row to dictionary."""
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'ticker': row['ticker'],
            'strategy': row['strategy'],
            'parameters': json.loads(row['parameters_json']),
            'interval': row['interval'],
            'cash': row['cash'],
            'active': bool(row['active']),
            'current_value': row['current_value'],
            'pnl': row['pnl'],
            'return_pct': row['return_pct'],
            'created_at': row['created_at'],
            'last_updated': row['last_updated']
        }

    def _position_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert position database row to dictionary."""
        return {
            'id': row['id'],
            'watchlist_id': row['watchlist_id'],
            'position_type': row['position_type'],
            'entry_date': row['entry_date'],
            'entry_price': row['entry_price'],
            'size': row['size'],
            'exit_date': row['exit_date'],
            'exit_price': row['exit_price'],
            'pnl': row['pnl'],
            'status': row['status']
        }
