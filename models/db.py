import sqlite3
from typing import Tuple

class DatabaseManager:
    """مدیریت عملیات دیتابیس SQLite"""

    def __init__(self, db_file: str):
        self.db_file = db_file
        self._create_tables()

    def _connect(self):
        """اتصال به دیتابیس"""
        return sqlite3.connect(self.db_file)

    def _create_tables(self):
        """ایجاد جدول‌ها در دیتابیس"""
        conn = self._connect()
        cursor = conn.cursor()

        # ایجاد جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                chat_id INTEGER UNIQUE,
                flags TEXT DEFAULT "000"
            )
        ''')

        # ایجاد جدول تنظیمات برای ذخیره offset
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # ایجاد جدول اطلاعات (informations)
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
        """اجرای یک query دیتابیس"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_all(self, query: str, params: Tuple = ()):
        """دریافت تمام داده‌ها از یک query"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def fetch_one(self, query: str, params: Tuple = ()):
        """دریافت یک ردیف از دیتابیس"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
