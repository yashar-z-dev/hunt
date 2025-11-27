from typing import List, Optional, Callable
import logging

from models.users import UserManager
from configs.bot_config import BotConfig
from configs.typing_utils import Command
from core.broadcast import Do_Broadcast

class TelegramBot:
    """BOT manager"""
    def __init__(self, 
                 config: BotConfig, 
                 user_manager: UserManager):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.secret = config.SECRET
        self.user_manager = user_manager

        self.CMD: List[Command] = [
            Command(keywords=["/secret", "/removed", "/added", "/common"], method=self.auth),
            Command(keywords=["/help"], method=self.help_command),
            Command(keywords=["/new"], method=self.new_command),
            Command(keywords=["/status"], method=self.status_command),
        ]

    def dispatch(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> Optional[str]:
        for cmd in self.CMD:
            for keyword in cmd.keywords:
                if text.startswith(keyword):
                    return cmd.method(id, chat_id, timestamp, flags, text)
        return "❌ Unknown command"

    def help_command(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> str:
        all_keywords = []
        for cmd in self.CMD:
            all_keywords.extend(cmd.keywords)
        all_keywords = sorted(set(all_keywords))
        return "\n".join(all_keywords)

    def new_command(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> None:
        self.logger.info("use: class Do_Broadcast in main")
        broadcaster = Do_Broadcast()
        broadcaster.run()
        return None

    def status_command(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> str:
        users = self.user_manager.get_all_users()
        all_users = []
        for user in users:
            all_users.append(f"{user.id}:")
            all_users.append(f"{user.chat_id}")
            all_users.append(f"{user.flags}")
            all_users.append(f"{user.timestamp}")
        return "\n".join(all_users)

    def auth(self, id: int, chat_id: int, timestamp: str, flags: str, text: str) -> str:
        updated_flags = list(flags)
        if text == f"/secret:{self.secret}":
            updated_flags = ['1', '1', '1', '1']
        elif text.startswith("/removed"):
            updated_flags[1] = '1' if updated_flags[1] == '0' else '0'
        elif text.startswith("/added"):
            updated_flags[2] = '1' if updated_flags[2] == '0' else '0'
        elif text.startswith("/common"):
            updated_flags[3] = '1' if updated_flags[3] == '0' else '0'

        new_flags = ''.join(updated_flags)
        self.user_manager.update_flags(chat_id=chat_id, new_flags=new_flags)
        return f"Flags updated to {new_flags}"
