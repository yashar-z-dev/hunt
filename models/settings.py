from models.db import DatabaseManager

class SettingsManager:
    """manage settings TABLE"""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_offset(self) -> int:
        query = "SELECT value FROM settings WHERE key = 'offset'"
        result = self.db_manager.fetch_one(query)
        return int(result[0]) if result else None

    def set_offset(self, offset: int):
        query = "REPLACE INTO settings (key, value) VALUES ('offset', ?)"
        self.db_manager.execute(query, (str(offset),))
