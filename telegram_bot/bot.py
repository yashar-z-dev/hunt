import time
from configs.config import Config
from models.users import UserManager, User
from models.settings import SettingsManager
import requests

from extract_data.diff_checker import diff_to_dict, build_message_custom

class TelegramBot:
    """BOT manager"""
    def __init__(self, 
                 config: Config, 
                 user_manager: UserManager, 
                 settings_manager: SettingsManager):

        self.token = config.TOKEN
        self.secret = config.SECRET
        self.base_url = config.BASE_URL
        self.timeout = config.TIMEOUT
        self.delay = config.DELAY
        self.limit = config.LIMIT
        self.user_manager = user_manager
        self.settings_manager = settings_manager

    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {'offset': offset, 'timeout': self.timeout}
        response = requests.get(url, params=params)
        return response.json()

    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        response = requests.get(url, params=params)
        return response.json()

    def process_received_messages(self, updates):
        for update in updates['result']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']

            # add_user(user) if not user in DB
            user = self.user_manager.get_user(chat_id)
            if not user:
                user = User(chat_id)
                self.user_manager.add_user(user)
                self.send_message(chat_id, f"You must subscribe to use this robot.\n{text}")
                return

            self.auth(chat_id=user.chat_id, flags=user.flags, text=text)
            result = self.user_manager.get_user(chat_id=chat_id)
            self.send_message(chat_id, f"{user.id}: UPDATED. {result.flags}")

    def send_broadcast(self, data: str, last_data: str="", all=False):
        users = self.user_manager.get_all_users()
        if all:
            for user in users:
                self.send_message(user.chat_id, data)
                time.sleep(self.limit)
        else:
            for user in users:
                if user.flags.startswith("1"):

                    diff_result: dict = diff_to_dict(first=data, second=last_data)
                    message = build_message_custom(user_data=user.flags, message=diff_result)

                    self.send_message(user.chat_id, message)
                else:
                    self.send_message(user.chat_id, f"{data}\n{user.flags}")
                time.sleep(self.limit)

    def run_message_processor(self, offset=None):
        updates = self.get_updates(offset=offset)
        if updates['result']:
            self.process_received_messages(updates)
            # return last update_id for set offset 
            new_offset = updates['result'][-1]['update_id'] + 1
            self.settings_manager.set_offset(new_offset)  # update new offset
            
            return new_offset
        return offset

    def auth(self, chat_id: int, flags: str, text: str):
        if not text:
            return "DEBUG, __EMPTY__"
        
        updated_flags = list(flags)
        if text == self.secret:
            updated_flags = ['1', '1', '1', '1']

        elif text.startswith("removed"):
            updated_flags[1] = '1' if updated_flags[1] == '0' else '0'

        elif text.startswith("added"):
            updated_flags[2] = '1' if updated_flags[2] == '0' else '0'

        elif text.startswith("common"):
            updated_flags[3] = '1' if updated_flags[3] == '0' else '0'

        new_flags = ''.join(updated_flags)
        
        self.user_manager.update_flags(chat_id=chat_id, new_flags=new_flags)

        return f"Flags updated to {new_flags}"
