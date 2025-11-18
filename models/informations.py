from datetime import datetime
from typing import Optional
from models.db import DatabaseManager

class InformationDateManager:
    """manage information TABLE"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_last_information(self, last: int = 1) -> list:
        """get last data with counter variable last"""
        query = "SELECT id, timestamp, data FROM informations ORDER BY timestamp DESC LIMIT ?"
        return self.db_manager.fetch_all(query, (last,))

    def get_all_in_date(self, 
                        year: Optional[int] = None, 
                        month: Optional[int] = None, 
                        day: Optional[int] = None) -> list:
        """get data with time parameter"""
        if year and month and day:
            start_date = f"{year}-{month:02d}-{day:02d} 00:00:00"
            end_date = f"{year}-{month:02d}-{day:02d} 23:59:59"
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        elif year and month:
            start_date = f"{year}-{month:02d}-01 00:00:00"
            end_date = f"{year}-{month:02d}-28 23:59:59"
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        elif year:
            start_date = f"{year}-01-01 00:00:00"
            end_date = f"{year}-12-31 23:59:59"
            query = "SELECT id, timestamp, data FROM informations WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp"
            params = (start_date, end_date)
        
        else:
            query = "SELECT id, timestamp, data FROM informations ORDER BY timestamp"
            params = ()

        return self.db_manager.fetch_all(query, params)

    def add_information(self, data: str):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        query = "INSERT INTO informations (timestamp, data) VALUES (?, ?)"
        self.db_manager.execute(query, (formatted_time, data))
