from typing import Optional
import time
import requests
import logging

from core.bot import TelegramBot
from models.db import DatabaseManager
from models.settings import SettingsManager
from models.informations import InformationDateManager
from models.users import UserManager, User
from configs.bot_config import BotConfig
from views.network_utils import split_message

class BotRunner:
    """
    handle command with long polling and keep alive the bot with loop
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger per class

        self.config = BotConfig()
        self.db_manager = DatabaseManager(self.config.DB_FILE)
        self.user_manager = UserManager(db_manager=self.db_manager)
        self.settings_manager = SettingsManager(db_manager=self.db_manager)
        self.information_manager = InformationDateManager(db_manager=self.db_manager)
        self.bot = TelegramBot(
            config=self.config,
            user_manager=self.user_manager
        )

        # Status
        self.offset: Optional[int] = self.settings_manager.get_offset()

    def get_updates(self, offset=None) -> dict:
        """
        big O = (self.config.TIMEOUT)
        """

        # send requests
        url = f"{self.config.BASE_URL}/getUpdates"
        params = {'offset': offset, 'timeout': self.config.TIMEOUT}

        try:
            response = requests.get(url, params=params)
        except Exception as e:
            self.logger.error(f"Error while getting updates: {e}")
            self.ERR_HANDELER() # Network Error
            return {}

        return response.json()

    def send_message(self, chat_id: int, text: str):
        """
        big O = (self.config.LIMIT)
        """
        # split if len(text) >= 4096
        messages: list[str] = split_message(text)

        for chunk in messages:
            url = f"{self.config.BASE_URL}/sendMessage"
            params = {'chat_id': chat_id, 'text': chunk}
            response = requests.get(url, params=params)

            result: dict = response.json()
            if result.get("ok"):
                self.logger.info(f"Message part sent successfully to chat_id {chat_id}.")
            else:
                error_description = result.get("description", "No error description provided.")
                self.logger.error(f"Error sending message part to chat_id {chat_id}: {error_description}")

            time.sleep(self.config.LIMIT)

    def process_commands(self, updates):
        for update in updates['result']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']

            # add_user(user) if not user in DB
            user = self.user_manager.get_user(chat_id)
            if not user:
                user = User(chat_id)
                self.user_manager.add_user(user)
                self.send_message(chat_id, f"{self.config.WHEN_no_auth_replay}\n{text}")
                self.logger.info(f"New user added with chat_id {chat_id}")
                return

            self.logger.debug(f"user text is:\n{text}")
            result = self.bot.dispatch(chat_id=user.chat_id, flags=user.flags, text=text)
            if result:
                self.logger.info(f"Processing result for chat_id {chat_id}")
                self.logger.debug(f"{result}")
                self.send_message(chat_id, f"{result}")

    def message_processor(self, offset: Optional[int]=None) -> Optional[int]:
        updates = self.get_updates(offset=offset)

        if updates.get('result', []):
            self.process_commands(updates)

            last_update = updates.get('result', [])[-1]
            new_offset = last_update.get('update_id', None)

            if new_offset is not None:
                new_offset += 1
                self.settings_manager.set_offset(new_offset)  # update new offset
                self.logger.info(f"Offset updated to {new_offset}")
                return new_offset

        return offset

    def process_messages(self):
        self.offset = self.message_processor(self.offset)

    def ERR_HANDELER(self):
        time.sleep(self.config.LIMIT)

    def run(self):
        # Main Loop
        while True:
            self.process_messages()

if __name__ == "__main__":
    # Logger setup for class with class name
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    bot = BotRunner()
    bot.run()