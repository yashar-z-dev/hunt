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

            # پاسخ به پیام
            self.send_message(chat_id, f"پیام شما: {text}")

    def send_broadcast(self, message):
        """ارسال پیام برودکست به تمام کاربران موجود در دیتابیس"""
        users = self.user_manager.get_all_users()
        for user in users:
            self.send_message(user.chat_id, message)
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

    def run_broadcast_scheduler(self):
        """اجرای ارسال پیام برودکست در زمان‌های مشخص"""
        # ارسال پیام‌های برودکست به تمام کاربران
        self.send_broadcast("این یک پیام برودکست است.")

    def main_loop(self):
        """حلقه اصلی ربات برای اجرای منظم"""
        offset = self.settings_manager.get_offset()  # دریافت offset از دیتابیس
        while True:
            # اجرای پردازش پیام‌ها و به روز رسانی offset
            offset = self.run_message_processor(offset)
            self.run_broadcast_scheduler()
            time.sleep(self.delay)
