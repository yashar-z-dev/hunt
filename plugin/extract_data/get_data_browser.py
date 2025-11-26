# 1/10
from playwright.sync_api import sync_playwright

from configs.browser_config import BrowserConfig

def fetch_from_browser(config: BrowserConfig):
    return {"error": f"Browser fetch failed"}