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
        data: str = get_extracet(debug=False, all=True)
        self.information_manager.add_information(data)
        last_data = self.information_manager.get_last_information(1)[0][2]
        return data, last_data


    def send_broadcast_if_due(self, 
                              data: Optional[str] = None, # dev here
                              force: bool=False
                              ):
        now = time.time()
        if force:
            data, last_data = self.update_information() # update and send new data

            self.bot.send_broadcast(data=data, last_data=last_data, all=False)
            self.last_broadcast_time = now
            print(f"✅ Broadcast sent at {datetime.datetime.now()}")

        elif now - self.last_broadcast_time >= self.config.broadcast_interval:

            data, last_data = self.update_information() # update and send new data

            self.bot.send_broadcast(data=data, last_data=last_data, all=False)
            self.last_broadcast_time = now
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
