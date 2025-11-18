# ==============================
# Example Usage
# ==============================
def ex(debug: bool, 
       all: bool) -> str:
    import json
    from extract_data.main_extractor import DataExtractor, CONFIG

    # parser.add_argument("-d", "--debug", action="store_true", help="Print detailed logs")
    # parser.add_argument("-a", "--all", action="store_true", help="Include archived/disabled/private programs too")

    # ساخت نمونه از کلاس با پارامتر include_all
    extractor = DataExtractor(config=CONFIG, include_all=all)
    results = extractor.extract()

    if isinstance(results, dict) and "error" in results:
        # اگر خطا بود
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    else:
        field_names = list(CONFIG["fields"].keys())

        if not debug:
            # خروجی تمیز برای pipeline (CSV-like)
            for p in results:
                values = [str(p.get(field, "")) for field in field_names]
                print(",".join(values))
        else:
            # خروجی انسان‌خوان برای دیباگ
            print("\n==========================")
            print(f"[📦] Finished! Total programs collected: {len(results)}")
            print("==========================\n")
            for idx, p in enumerate(results, 1):
                values = [f"{field}: {p.get(field, '')}" for field in field_names]
                print(f"{idx:02d}. " + " — ".join(values))

    return "ERROR"

#############################################################

def main():
    import time
    from configs.config import Config
    from telegram_bot.bot import UserManager
    from telegram_bot.bot import TelegramBot
    from models.settings import SettingsManager
    from models.db import DatabaseManager

    config = Config()
    yeswehack: str = ex(debug=True, all=True)
    # ایجاد نمونه از کلاس UserManager
    db_manager = DatabaseManager(config.DB_FILE)
    user_manager = UserManager(db_manager=db_manager)
    settings_manager = SettingsManager(db_manager=db_manager)
    # ایجاد نمونه از کلاس TelegramBot
    bot = TelegramBot(config=config, 
                      user_manager=user_manager, 
                      settings_manager=settings_manager)

    """حلقه اصلی ربات برای اجرای منظم"""
    offset = bot.settings_manager.get_offset() # دریافت offset از دیتابیس
    while True:
        # اجرای پردازش پیام‌ها و به روز رسانی offset
        offset = bot.run_message_processor(offset)
        bot.send_broadcast(message=yeswehack, all=False)
        time.sleep(bot.delay)

if __name__ == "__main__":
    main()
