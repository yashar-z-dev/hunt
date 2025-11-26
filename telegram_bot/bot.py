from typing import List, Optional
from configs.bot_config import BotConfig
from models.users import UserManager
from models.settings import SettingsManager
from configs.typing_utils import Command

class TelegramBot:
    """BOT manager"""
    def __init__(self, 
                 config: BotConfig, 
                 user_manager: UserManager, 
                 settings_manager: SettingsManager):

        self.secret = config.SECRET
        self.user_manager = user_manager
        self.settings_manager = settings_manager

        self.CMD: List[Command] = [
            Command(keywords=["secret", "removed", "added", "common"], 
                    method=self.auth),
            Command(keywords=["new", "help"], 
                    method=self.handle_another_commands)
        ]

    def split_message(self, text: str, max_length: int = 4096) -> list[str]:
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

    def dispatch(self, chat_id: int, flags: str, text: str) -> Optional[str]:
        for cmd in self.CMD:
            for keyword in cmd.keywords:
                if text.startswith(keyword):
                    return cmd.method(chat_id=chat_id, flags=flags, text=text)

        return "❌ Unknown command"

    def handle_another_commands(self, chat_id: int, flags: str, text: str) -> Optional[str]:
        """ ["new", "help"] """
        if text.startswith("new"):
            return "now can't exec this command."

        if text.startswith("help"):
            all_keywords = []
            for cmd in self.CMD:
                all_keywords.extend(cmd.keywords)

            all_keywords = sorted(set(all_keywords))

            keywords_str = "\n".join(all_keywords)
            return keywords_str

    def auth(self, chat_id: int, flags: str, text: str) -> Optional[str]:
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
