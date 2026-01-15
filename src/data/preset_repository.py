import os
import sqlite3
import datetime
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class PresetRepository:
    """Repository for persisting and querying strategy presets."""

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
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(name, strategy, ticker)
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_preset_ticker ON strategy_presets(ticker)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_preset_strategy ON strategy_presets(strategy)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_preset_name ON strategy_presets(name)
            ''')

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_preset(self, preset_data: Dict[str, Any]) -> int:
        """
        Create a new strategy preset.

        Args:
            preset_data: Dictionary containing preset details:
                - name (str): Name of the preset
                - ticker (str): Ticker symbol
                - strategy (str): Strategy name
                - parameters (dict): Strategy parameters
                - interval (str): Time interval
                - notes (str, optional): Optional notes

        Returns:
            int: The ID of the created preset

        Raises:
            sqlite3.IntegrityError: If preset with same (name, strategy, ticker) exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            parameters_json = json.dumps(preset_data.get('parameters', {}))
            created_at = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO strategy_presets (
                    name, ticker, strategy, parameters_json, interval, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                preset_data['name'],
                preset_data['ticker'],
                preset_data['strategy'],
                parameters_json,
                preset_data['interval'],
                preset_data.get('notes'),
                created_at
            ))

            conn.commit()
            return cursor.lastrowid

    def get_preset(self, preset_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific preset by its ID.

        Args:
            preset_id: The preset ID

        Returns:
            Dictionary containing preset details, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM strategy_presets WHERE id = ?', (preset_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_dict(row)

    def list_presets(self, ticker: Optional[str] = None, strategy: Optional[str] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List saved presets with optional filters.

        Args:
            ticker: Filter by ticker (optional)
            strategy: Filter by strategy (optional)
            limit: Maximum number of results (default: 100)
            offset: Number of results to skip (default: 0)

        Returns:
            List of preset dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM strategy_presets WHERE 1=1'
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

    def delete_preset(self, preset_id: int) -> bool:
        """
        Delete a preset by ID.

        Args:
            preset_id: The preset ID to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM strategy_presets WHERE id = ?', (preset_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_preset_count(self, ticker: Optional[str] = None, strategy: Optional[str] = None) -> int:
        """
        Get the total count of presets matching the filters.

        Args:
            ticker: Filter by ticker (optional)
            strategy: Filter by strategy (optional)

        Returns:
            Total count of matching presets
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT COUNT(*) FROM strategy_presets WHERE 1=1'
            params = []

            if ticker:
                query += ' AND ticker = ?'
                params.append(ticker)

            if strategy:
                query += ' AND strategy = ?'
                params.append(strategy)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def preset_exists(self, name: str, strategy: str, ticker: str) -> bool:
        """
        Check if a preset with the given name, strategy, and ticker already exists.

        Args:
            name: Preset name
            strategy: Strategy name
            ticker: Ticker symbol

        Returns:
            True if preset exists, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM strategy_presets WHERE name = ? AND strategy = ? AND ticker = ?',
                (name, strategy, ticker)
            )
            return cursor.fetchone()[0] > 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a dictionary."""
        result = dict(row)
        result['parameters'] = json.loads(result['parameters_json'])
        del result['parameters_json']
        return result
