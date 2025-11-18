import time
from configs.config import Config
from models.db import DatabaseManager
from telegram_bot.bot import UserManager
from models.settings import SettingsManager
from models.informations import InformationDateManager
from telegram_bot.bot import TelegramBot
from extract_data.main_extractor import get_extracet

def main():
    config = Config()
    db_manager = DatabaseManager(config.DB_FILE)
    user_manager = UserManager(db_manager=db_manager)
    settings_manager = SettingsManager(db_manager=db_manager)
    information_manager = InformationDateManager(db_manager=db_manager)
    bot = TelegramBot(config=config, 
                      user_manager=user_manager, 
                      settings_manager=settings_manager)

    """main loop"""
    offset = bot.settings_manager.get_offset() # get offset as db
    last_data = ""
    while True:
        offset = bot.run_message_processor(offset)

        data: str = get_extracet(debug=True, all=True)
        information_manager.add_information(data)
        last_data = information_manager.get_last_information(1)
        if not last_data:
            last_data = ""

        bot.send_broadcast(message=data, 
                           last_data=last_data, 
                           all=False)
        time.sleep(bot.delay)

if __name__ == "__main__":
    main()
