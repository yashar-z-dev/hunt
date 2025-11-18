# ==============================
# Example Usage
# ==============================
def ex():
    import argparse
    import json
    from extract_data.main_extractor import DataExtractor, CONFIG

    parser = argparse.ArgumentParser(description="Fetch YesWeHack programs via API/Browser")
    parser.add_argument("-d", "--debug", action="store_true", help="Print detailed logs")
    parser.add_argument("-a", "--all", action="store_true", help="Include archived/disabled/private programs too")
    args = parser.parse_args()

    # ساخت نمونه از کلاس با پارامتر include_all
    extractor = DataExtractor(config=CONFIG, include_all=args.all)
    results = extractor.extract()

    if isinstance(results, dict) and "error" in results:
        # اگر خطا بود
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        field_names = list(CONFIG["fields"].keys())

        if not args.debug:
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


#############################################################

def main():
    from configs.config import Config
    from telegram_bot.bot import UserManager
    from telegram_bot.bot import TelegramBot
    config = Config()
    
    # ایجاد نمونه از کلاس UserManager
    user_manager = UserManager(config.DB_FILE)
    
    # ایجاد نمونه از کلاس TelegramBot
    bot = TelegramBot(config, user_manager)
    
    # اجرای حلقه اصلی ربات
    bot.main_loop()

if __name__ == "__main__":
    main()
