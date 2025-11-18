from models.db import DatabaseManager
from typing import List, Optional
from datetime import datetime

class User:
    """نمایش یک کاربر و اطلاعات آن"""

    def __init__(self, chat_id: int, timestamp: str = None, flags: str = "0000"):
        self.id: Optional[int] = None  # مقدار id بعداً از دیتابیس دریافت می‌شود
        self.chat_id = chat_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.flags = flags

    def update_flags(self, new_flags: str):
        """به‌روزرسانی فیلد flags کاربر"""
        self.flags = new_flags

class UserManager:
    """مدیریت کاربران با استفاده از دیتابیس SQLite"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_user(self, user: User):
        """اضافه کردن یک کاربر جدید به دیتابیس"""
        query = '''INSERT INTO users (timestamp, chat_id, flags) 
                   VALUES (?, ?, ?)'''
        self.db_manager.execute(query, (user.timestamp, user.chat_id, user.flags))

    def get_user(self, chat_id: int) -> User:
        """دریافت یک کاربر از دیتابیس با استفاده از chat_id"""
        query = "SELECT id, timestamp, chat_id, flags FROM users WHERE chat_id = ?"
        result = self.db_manager.fetch_one(query, (chat_id,))
        if result:
            return User(chat_id=result[2], timestamp=result[1], flags=result[3])
        return None

    def get_all_users(self) -> List[User]:
        """دریافت تمام کاربران از دیتابیس"""
        query = "SELECT id, timestamp, chat_id, flags FROM users"
        results = self.db_manager.fetch_all(query)
        return [User(chat_id=row[2], timestamp=row[1], flags=row[3]) for row in results]

    def update_flags(self, chat_id: int, new_flags: str):
        """بروزرسانی فیلد flags یک کاربر"""
        query = "UPDATE users SET flags = ? WHERE chat_id = ?"
        self.db_manager.execute(query, (new_flags, chat_id))

    def get_offset(self) -> int:
        """دریافت آخرین offset ذخیره‌شده از دیتابیس"""
        query = "SELECT value FROM settings WHERE key = 'offset'"
        result = self.db_manager.fetch_one(query)
        return int(result[0]) if result else None

    def set_offset(self, offset: int):
        """ذخیره offset در دیتابیس"""
        query = "REPLACE INTO settings (key, value) VALUES ('offset', ?)"
        self.db_manager.execute(query, (str(offset),))
