from datetime import datetime
from typing import Optional, Tuple
from models.db import DatabaseManager

class InformationDateManager:
    """مدیریت اطلاعات مرتبط با تاریخ در دیتابیس"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_last_information(self, last: int = 1) -> list:
        """دریافت جدیدترین رکوردها (بر اساس تعداد مشخص شده)"""
        query = "SELECT id, timestamp, data FROM informations ORDER BY timestamp DESC LIMIT ?"
        return self.db_manager.fetch_all(query, (last,))

    def get_all_in_date(self, year: Optional[int] = None, month: Optional[int] = None, day: Optional[int] = None) -> list:
        """
        دریافت اطلاعات بر اساس تاریخ مشخص شده
        - اگر فقط year داده شود، تمام رکوردهای آن سال را برمی‌گرداند
        - اگر month هم داده شود، تمام رکوردهای آن ماه را برمی‌گرداند
        - اگر day هم داده شود، رکوردهای آن روز را برمی‌گرداند
        """
        # ساختن تاریخ شروع و پایان
        if year and month and day:
            # اگر سال، ماه و روز داده شده باشد
            start_date = f"{year}-{month:02d}-{day:02d} 00:00:00"
            end_date = f"{year}-{month:02d}-{day:02d} 23:59:59"
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        elif year and month:
            # اگر فقط سال و ماه داده شده باشد
            start_date = f"{year}-{month:02d}-01 00:00:00"
            end_date = f"{year}-{month:02d}-28 23:59:59"  # ساده‌سازی: در صورتی که ماه 31 روزی باشد باید به طور جداگانه بررسی شود
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        elif year:
            # اگر فقط سال داده شده باشد
            start_date = f"{year}-01-01 00:00:00"
            end_date = f"{year}-12-31 23:59:59"
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        else:
            # اگر هیچ تاریخ خاصی داده نشده باشد (تمام داده‌های موجود)
            query = "SELECT id, timestamp, data FROM informations ORDER BY timestamp"
            params = ()

        return self.db_manager.fetch_all(query, params)

    def add_information(self, timestamp: str, data: str):
        """افزودن یک رکورد جدید به جدول informations"""
        query = "INSERT INTO informations (timestamp, data) VALUES (?, ?)"
        self.db_manager.execute(query, (timestamp, data))
