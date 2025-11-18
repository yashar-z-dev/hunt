import time
from configs.config import Config
from models.users import UserManager, User
from models.settings import SettingsManager
import requests

class TelegramBot:
    """کلاس اصلی ربات تلگرام که وظیفه پردازش پیام‌ها و ارسال‌ها را دارد"""

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
        """دریافت پیام‌های جدید از تلگرام (با timeout کوتاه برای long polling)"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': offset, 'timeout': self.timeout}
        response = requests.get(url, params=params)
        return response.json()

    def send_message(self, chat_id, text):
        """ارسال پیام به یک کاربر خاص"""
        url = f"{self.base_url}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        response = requests.get(url, params=params)
        return response.json()

    def process_received_messages(self, updates):
        """پردازش پیام‌های دریافتی از کاربران"""
        for update in updates['result']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']

            # اضافه کردن کاربر جدید به دیتابیس (در صورت عدم وجود)
            user = self.user_manager.get_user(chat_id)
            if not user:
                user = User(chat_id)
                self.user_manager.add_user(user)
                self.send_message(chat_id, f"برای استفاده از این ربات باید اشتراک تهیه نمایید.\n{text}")
                return

            self.auth(chat_id=user.chat_id, flags=user.flags, text=text)
            result = self.user_manager.get_user(chat_id=chat_id)
            self.send_message(chat_id, f"{user.id}: UPDATED. {result.flags}")

    def send_broadcast(self, message: str, all=False):
        """ارسال پیام برودکست به تمام کاربران موجود در دیتابیس"""
        users = self.user_manager.get_all_users()
        if all:
            for user in users:
                self.send_message(user.chat_id, message)
                time.sleep(self.limit)
        else:
            for user in users:
                if user.flags.startswith("1"):
                    self.send_message(user.chat_id, message)
                else:
                    self.send_message(user.chat_id, f"{message}\n{user.flags}")
                time.sleep(self.limit)

    def run_message_processor(self, offset=None):
        """اجرای پردازش پیام‌ها"""
        updates = self.get_updates(offset=offset)
        if updates['result']:
            # پردازش پیام‌های دریافتی
            self.process_received_messages(updates)
            
            # برگرداندن آخرین update_id برای تنظیم offset
            new_offset = updates['result'][-1]['update_id'] + 1
            self.settings_manager.set_offset(new_offset)  # ذخیره offset جدید
            
            return new_offset
        return offset

    def auth(self, chat_id: int, flags: str, text: str):
        if not text:
            return "DEBUG, __EMPTY__"
        if text=="1234567890":
            self.user_manager.update_flags(chat_id=chat_id, new_flags="1111")
        elif text.startswith("removed"):
            self.user_manager.update_flags(chat_id=chat_id, new_flags="1100")
        elif text.startswith("added"):
            self.user_manager.update_flags(chat_id=chat_id, new_flags="1010")
        elif text.startswith("common"):
            self.user_manager.update_flags(chat_id=chat_id, new_flags="1001")
        elif text.startswith("both"):
            self.user_manager.update_flags(chat_id=chat_id, new_flags="1110")