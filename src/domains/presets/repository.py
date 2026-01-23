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
                'presets.db'
            )

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    strategy TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    cash REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(name)
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategy ON presets(strategy)')
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

    def create_preset(self, preset_data: Dict[str, Any]) -> int:
        """Create a new preset and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO presets (name, description, strategy, parameters_json, interval, cash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                preset_data['name'],
                preset_data.get('description'),
                preset_data['strategy'],
                json.dumps(preset_data['parameters']),
                preset_data['interval'],
                preset_data['cash'],
                now,
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def get_preset_by_id(self, preset_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a preset by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM presets WHERE id = ?', (preset_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def get_preset_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a preset by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM presets WHERE name = ?', (name,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def list_presets(self, strategy: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all presets with optional strategy filter."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if strategy:
                cursor.execute(
                    'SELECT * FROM presets WHERE strategy = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?',
                    (strategy, limit, offset)
                )
            else:
                cursor.execute(
                    'SELECT * FROM presets ORDER BY updated_at DESC LIMIT ? OFFSET ?',
                    (limit, offset)
                )

            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update_preset(self, preset_id: int, updates: Dict[str, Any]) -> bool:
        """Update a preset. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic update query
            set_clauses = []
            values = []

            if 'name' in updates:
                set_clauses.append('name = ?')
                values.append(updates['name'])
            if 'description' in updates:
                set_clauses.append('description = ?')
                values.append(updates['description'])
            if 'parameters' in updates:
                set_clauses.append('parameters_json = ?')
                values.append(json.dumps(updates['parameters']))
            if 'interval' in updates:
                set_clauses.append('interval = ?')
                values.append(updates['interval'])
            if 'cash' in updates:
                set_clauses.append('cash = ?')
                values.append(updates['cash'])

            if not set_clauses:
                return False

            set_clauses.append('updated_at = ?')
            values.append(datetime.datetime.now().isoformat())
            values.append(preset_id)

            query = f"UPDATE presets SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0

    def delete_preset(self, preset_id: int) -> bool:
        """Delete a preset. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM presets WHERE id = ?', (preset_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_preset_count(self, strategy: Optional[str] = None) -> int:
        """Get total count of presets."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if strategy:
                cursor.execute('SELECT COUNT(*) FROM presets WHERE strategy = ?', (strategy,))
            else:
                cursor.execute('SELECT COUNT(*) FROM presets')
            return cursor.fetchone()[0]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'strategy': row['strategy'],
            'parameters': json.loads(row['parameters_json']),
            'interval': row['interval'],
            'cash': row['cash'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
