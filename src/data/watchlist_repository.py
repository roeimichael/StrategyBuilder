import os
import sqlite3
import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class WatchlistRepository:
    """Repository for managing watchlist entries for automated strategy monitoring."""

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
        """Create database and watchlist_entries table if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    preset_id INTEGER,
                    run_id INTEGER,
                    frequency TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_run_at TEXT,
                    FOREIGN KEY (preset_id) REFERENCES strategy_presets(id),
                    FOREIGN KEY (run_id) REFERENCES strategy_runs(id),
                    CHECK (preset_id IS NOT NULL OR run_id IS NOT NULL)
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_watchlist_preset ON watchlist_entries(preset_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_watchlist_run ON watchlist_entries(run_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_watchlist_enabled ON watchlist_entries(enabled)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_watchlist_frequency ON watchlist_entries(frequency)
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

    def create_entry(self, entry_data: Dict[str, Any]) -> int:
        """
        Create a new watchlist entry.

        Args:
            entry_data: Dictionary containing:
                - name (str): Descriptive name for the entry
                - preset_id (int, optional): Reference to a preset
                - run_id (int, optional): Reference to a saved run
                - frequency (str): Frequency (e.g., 'daily', 'intraday_15m')
                - enabled (bool): Whether the entry is active

        Returns:
            int: The ID of the created entry

        Raises:
            ValueError: If neither preset_id nor run_id is provided
        """
        if not entry_data.get('preset_id') and not entry_data.get('run_id'):
            raise ValueError("Either preset_id or run_id must be provided")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            created_at = datetime.datetime.now().isoformat()
            enabled = 1 if entry_data.get('enabled', True) else 0

            cursor.execute('''
                INSERT INTO watchlist_entries (
                    name, preset_id, run_id, frequency, enabled, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entry_data['name'],
                entry_data.get('preset_id'),
                entry_data.get('run_id'),
                entry_data['frequency'],
                enabled,
                created_at
            ))

            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a watchlist entry by ID.

        Args:
            entry_id: The watchlist entry ID

        Returns:
            Dictionary with entry details or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, preset_id, run_id, frequency, enabled, created_at, last_run_at
                FROM watchlist_entries
                WHERE id = ?
            ''', (entry_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'preset_id': row['preset_id'],
                    'run_id': row['run_id'],
                    'frequency': row['frequency'],
                    'enabled': bool(row['enabled']),
                    'created_at': row['created_at'],
                    'last_run_at': row['last_run_at']
                }
            return None

    def list_entries(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        List all watchlist entries.

        Args:
            enabled_only: If True, only return enabled entries

        Returns:
            List of entry dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if enabled_only:
                cursor.execute('''
                    SELECT id, name, preset_id, run_id, frequency, enabled, created_at, last_run_at
                    FROM watchlist_entries
                    WHERE enabled = 1
                    ORDER BY created_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, name, preset_id, run_id, frequency, enabled, created_at, last_run_at
                    FROM watchlist_entries
                    ORDER BY created_at DESC
                ''')

            rows = cursor.fetchall()
            return [{
                'id': row['id'],
                'name': row['name'],
                'preset_id': row['preset_id'],
                'run_id': row['run_id'],
                'frequency': row['frequency'],
                'enabled': bool(row['enabled']),
                'created_at': row['created_at'],
                'last_run_at': row['last_run_at']
            } for row in rows]

    def update_entry(self, entry_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a watchlist entry.

        Args:
            entry_id: The entry ID
            updates: Dictionary of fields to update

        Returns:
            bool: True if updated, False if entry not found
        """
        allowed_fields = ['name', 'enabled', 'frequency', 'last_run_at']
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            return False

        # Convert enabled to integer if present
        if 'enabled' in update_fields:
            update_fields['enabled'] = 1 if update_fields['enabled'] else 0

        with self._get_connection() as conn:
            cursor = conn.cursor()

            set_clause = ', '.join([f'{field} = ?' for field in update_fields.keys()])
            values = list(update_fields.values()) + [entry_id]

            cursor.execute(f'''
                UPDATE watchlist_entries
                SET {set_clause}
                WHERE id = ?
            ''', values)

            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a watchlist entry.

        Args:
            entry_id: The entry ID to delete

        Returns:
            bool: True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM watchlist_entries WHERE id = ?', (entry_id,))
            conn.commit()

            return cursor.rowcount > 0

    def update_last_run(self, entry_id: int) -> bool:
        """
        Update the last_run_at timestamp for an entry.

        Args:
            entry_id: The entry ID

        Returns:
            bool: True if updated
        """
        return self.update_entry(entry_id, {'last_run_at': datetime.datetime.now().isoformat()})

    def get_entries_by_frequency(self, frequency: str, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all watchlist entries for a specific frequency.

        Args:
            frequency: The frequency to filter by (e.g., 'daily', 'intraday_15m')
            enabled_only: If True, only return enabled entries

        Returns:
            List of entry dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if enabled_only:
                cursor.execute('''
                    SELECT id, name, preset_id, run_id, frequency, enabled, created_at, last_run_at
                    FROM watchlist_entries
                    WHERE frequency = ? AND enabled = 1
                    ORDER BY created_at DESC
                ''', (frequency,))
            else:
                cursor.execute('''
                    SELECT id, name, preset_id, run_id, frequency, enabled, created_at, last_run_at
                    FROM watchlist_entries
                    WHERE frequency = ?
                    ORDER BY created_at DESC
                ''', (frequency,))

            rows = cursor.fetchall()
            return [{
                'id': row['id'],
                'name': row['name'],
                'preset_id': row['preset_id'],
                'run_id': row['run_id'],
                'frequency': row['frequency'],
                'enabled': bool(row['enabled']),
                'created_at': row['created_at'],
                'last_run_at': row['last_run_at']
            } for row in rows]
