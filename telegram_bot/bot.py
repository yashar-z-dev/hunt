import time
from configs.bot_config import BotConfig
from models.users import UserManager, User
from models.settings import SettingsManager
import requests

from UI.diff_checker import diff_to_dict, build_message_custom

class TelegramBot:
    """BOT manager"""
    def __init__(self, 
                 config: BotConfig, 
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

        self.CMD = [
            {"keywords": ["secret", "removed", "added", "common"], "method": self.auth},
            {"keywords": ["new", "help"], "method": self.handle_another_commands}
            ]

    def get_updates(self, offset=None):
        url = f"{self.base_url}/getUpdates"
        params = {'offset': offset, 'timeout': self.timeout}
        response = requests.get(url, params=params)
        return response.json()

    def split_message(self, text: str, max_length: int = 4096) -> list:
        lines = text.split("\n")
        current_message = ""
        messages = []

        for line in lines:
            if len(current_message) + len(line) + 1 <= max_length:
                current_message += ("\n" + line) if current_message else line
            else:
                messages.append(current_message)
                current_message = line

        if current_message:
            messages.append(current_message)

        return messages

    def send_message(self, chat_id: int, text: str):
        # split if len(text) >= 4096
        messages = self.split_message(text)

        for chunk in messages:
            url = f"{self.base_url}/sendMessage"
            params = {'chat_id': chat_id, 'text': chunk}
            response = requests.get(url, params=params)

            result: dict = response.json()
            if result.get("ok"):
                print(f"Message part sent successfully to chat_id {chat_id}.")
            else:
                error_description = result.get("description", "No error description provided.")
                print(f"Error sending message part to chat_id {chat_id}: {error_description}")
            
            time.sleep(self.limit)
            
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

            result = self.dispatch(chat_id=user.chat_id, flags=user.flags, text=text)
            if result:
                self.send_message(chat_id, f"{result}")

    def send_broadcast(self, data: str, last_data: str="", all=False):
        users = self.user_manager.get_all_users()
        if all:
            for user in users:
                self.send_message(user.chat_id, data)

                time.sleep(self.limit)
        else:
            for user in users:
                print(f"User chat_id: {user.chat_id}, flags: {user.flags}")

                if user.flags.startswith("1"):

                    diff_result: dict = diff_to_dict(first=data, second=last_data)
                    message = build_message_custom(user_data=user.flags, message=diff_result)

                    self.send_message(user.chat_id, message)
                else:
                    self.send_message(user.chat_id, f"{len(data)}\n{user.flags}")
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

    def dispatch(self, chat_id: int, flags: str, text: str):
        for cmd in self.CMD:
            if any(text.startswith(keyword) for keyword in cmd["keywords"]):
                return cmd["method"](chat_id=chat_id, flags=flags, text=text)
        return "❌ Unknown command"

    def handle_another_commands(self, chat_id: int, flags: str, text: str) -> None:
        """ ["new", "help"] """
        if text.startswith("new"):
            from main import BotRunner
            bot = BotRunner()
            bot.send_broadcast_if_due(force=True)
            return None

        elif text.startswith("help"):
            all_keywords = []
            for cmd in self.CMD:
                all_keywords.extend(cmd["keywords"])

            all_keywords = sorted(set(all_keywords))

            keywords_str = "\n".join(all_keywords)

            return keywords_str


    def auth(self, chat_id: int, flags: str, text: str) -> str:
        """ ["secret", "removed", "added", "common"] """
        updated_flags = list(flags)
        if text == f"secret:{self.secret}":
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
