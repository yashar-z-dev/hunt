from models.db import DatabaseManager

class SettingsManager:
    """مدیریت تنظیمات ربات (مانند offset)"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_offset(self) -> int:
        """دریافت مقدار offset از دیتابیس"""
        query = "SELECT value FROM settings WHERE key = 'offset'"
        result = self.db_manager.fetch_one(query)
        return int(result[0]) if result else None

    def set_offset(self, offset: int):
        """ذخیره مقدار offset در دیتابیس"""
        query = "REPLACE INTO settings (key, value) VALUES ('offset', ?)"
        self.db_manager.execute(query, (str(offset),))
