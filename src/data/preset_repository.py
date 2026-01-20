import os
import sqlite3
import datetime
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

class PresetRepository:
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

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_presets'")
            table_exists = cursor.fetchone()

            if table_exists:
                cursor.execute("PRAGMA table_info(strategy_presets)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'ticker' in columns:
                    cursor.execute('DROP TABLE strategy_presets')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(name, strategy)
                )
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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_preset(self, preset_data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            parameters_json = json.dumps(preset_data.get('parameters', {}))
            created_at = datetime.datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO strategy_presets (
                    name, strategy, parameters_json, notes, created_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                preset_data['name'],
                preset_data['strategy'],
                parameters_json,
                preset_data.get('notes'),
                created_at
            ))
            conn.commit()
            return cursor.lastrowid

    def get_preset(self, preset_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM strategy_presets WHERE id = ?', (preset_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(row)

    def list_presets(self, strategy: Optional[str] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM strategy_presets WHERE 1=1'
            params = []
            if strategy:
                query += ' AND strategy = ?'
                params.append(strategy)
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def delete_preset(self, preset_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM strategy_presets WHERE id = ?', (preset_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_preset_count(self, strategy: Optional[str] = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT COUNT(*) FROM strategy_presets WHERE 1=1'
            params = []
            if strategy:
                query += ' AND strategy = ?'
                params.append(strategy)
            cursor.execute(query, params)
            return cursor.fetchone()[0]

    def preset_exists(self, name: str, strategy: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM strategy_presets WHERE name = ? AND strategy = ?',
                (name, strategy)
            )
            return cursor.fetchone()[0] > 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        result = dict(row)
        result['parameters'] = json.loads(result['parameters_json'])
        del result['parameters_json']
        return result
