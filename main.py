from typing import Optional, Tuple
import time
import datetime
from configs.bot_config import BotConfig
from models.db import DatabaseManager
from telegram_bot.bot import UserManager, TelegramBot
from models.settings import SettingsManager
from models.informations import InformationDateManager
from extract_data.main_extractor import get_extracet


class BotRunner:
    def __init__(self):
        self.config = BotConfig()
        self.db_manager = DatabaseManager(self.config.DB_FILE)
        self.user_manager = UserManager(db_manager=self.db_manager)
        self.settings_manager = SettingsManager(db_manager=self.db_manager)
        self.information_manager = InformationDateManager(db_manager=self.db_manager)
        self.bot = TelegramBot(
            config=self.config,
            user_manager=self.user_manager,
            settings_manager=self.settings_manager
        )

        # Status
        self.offset: Optional[int] = self.bot.settings_manager.get_offset()
        self.last_broadcast_time: float = time.time()

    def process_messages(self):
        self.offset = self.bot.run_message_processor(self.offset)

    def update_information(self) -> Tuple[str, str]:
        """
        Backend logic note:
        - add_information() stores the new data into the database.
        - get_last_information() retrieves the most recent entry from the database.
        
        ⚠️ The order of operations is critical:
        We must fetch the last_data BEFORE inserting the new data.
        Otherwise, last_data would equal the freshly added data,
        and we would lose the actual previous record.
        """
        infos: list = self.information_manager.get_last_information(1)
        last_data: str = infos[0][2] if infos else ""

        data: Optional[str] = get_extracet(debug=False, include_all=True)
        if data is not None: # check not ERROR
            self.information_manager.add_information(data)
            return data, last_data

        return f"ERROR when get data as api: data: {data}", "ERROR" # fallback

    def send_broadcast_if_due(self, data: Optional[str] = None, force: bool=False):
        now = time.time()
        if force or now - self.last_broadcast_time >= self.config.broadcast_interval:
            self._do_broadcast()

    def _do_broadcast(self):
        data, last_data = self.update_information()
        self.bot.send_broadcast(data=data, last_data=last_data, all=False)
        self.last_broadcast_time = time.time()
        print(f"✅ Broadcast sent at {datetime.datetime.now()}")

    def run(self):
        # Main Loop
        while True:
            self.process_messages()

            self.send_broadcast_if_due()

            time.sleep(self.config.DELAY)

if __name__ == "__main__":
    runner = BotRunner()
    runner.run()
