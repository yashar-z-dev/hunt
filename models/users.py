from typing import List, Optional
from datetime import datetime

from models.db import DatabaseManager

class User:
    """show one user datails"""
    def __init__(self, chat_id: int, timestamp: Optional[str] = None, flags: str = "0000"):
        self.id: Optional[int] = None  # Runtime get as DB
        self.chat_id = chat_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.flags = flags

    def update_flags(self, new_flags: str):
        self.flags = new_flags

class UserManager:
    """manage users TABLE"""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_user(self, user: User):
        query = '''INSERT INTO users (timestamp, chat_id, flags) 
                   VALUES (?, ?, ?)'''
        self.db_manager.execute(query, (user.timestamp, user.chat_id, user.flags))

    def get_user(self, chat_id: int) -> Optional[User]:
        query = "SELECT id, timestamp, chat_id, flags FROM users WHERE chat_id = ?"
        result = self.db_manager.fetch_one(query, (chat_id,))
        if result:
            return User(chat_id=result[2], timestamp=result[1], flags=result[3])
        return None

    def get_all_users(self) -> List[User]:
        query = "SELECT id, timestamp, chat_id, flags FROM users"
        results = self.db_manager.fetch_all(query)
        return [User(chat_id=row[2], timestamp=row[1], flags=row[3]) for row in results]

    def update_flags(self, chat_id: int, new_flags: str):
        query = "UPDATE users SET flags = ? WHERE chat_id = ?"
        self.db_manager.execute(query, (new_flags, chat_id))