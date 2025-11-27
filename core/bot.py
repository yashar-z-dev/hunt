from typing import List, Optional
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
        
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger per class

        self.secret = config.SECRET
        self.user_manager = user_manager

        self.CMD: List[Command] = [
            Command(keywords=["secret", "removed", "added", "common"], 
                    method=self.auth),
            Command(keywords=["help", "new", "status"], 
                    method=self.handle_another_commands)
        ]

    def dispatch(self, chat_id: int, flags: str, text: str) -> Optional[str]:
        for cmd in self.CMD:
            for keyword in cmd.keywords:
                if text.startswith(keyword):
                    return cmd.method(chat_id=chat_id, flags=flags, text=text)

        return "❌ Unknown command"

    def handle_another_commands(self, chat_id: int, flags: str, text: str) -> Optional[str]:
        """ ["new", "help"] """
        if text.startswith("new"):
            self.logger.info(f"use: class Do_Broadcast in main")
            broadcaster = Do_Broadcast()
            broadcaster.run()
            return None

        elif text.startswith("help"):
            all_keywords = []
            for cmd in self.CMD:
                all_keywords.extend(cmd.keywords)

            all_keywords = sorted(set(all_keywords))

            keywords_str = "\n".join(all_keywords)
            return keywords_str
        
        elif text.startswith("status"):
            # get all users
            users = self.user_manager.get_all_users()
            all_users = []
            for user in users:
                all_users.append(f"{user.id}:")
                all_users.append(f"{user.chat_id}")
                all_users.append(f"{user.flags}")
                all_users.append(f"{user.timestamp}")
            
            all_users_str = "\n".join(all_users)
            return all_users_str
        
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
