import sqlite3
from typing import Tuple

class DatabaseManager:
    """manage SQLite DB"""
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._create_tables()

    def _connect(self):
        """Connect to DB"""
        return sqlite3.connect(self.db_file)

    def _create_tables(self):
        """Create TABLES"""
        conn = self._connect()
        cursor = conn.cursor()

        # Users TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                chat_id INTEGER UNIQUE,
                flags TEXT DEFAULT "0000"
            )
        ''')

        # Settings TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # informations TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS informations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def execute(self, query: str, params: Tuple = ()):
        """Run once query in DB"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_all(self, query: str, params: Tuple = ()):
        """get all data as once query"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def fetch_one(self, query: str, params: Tuple = ()):
        """get once line"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
