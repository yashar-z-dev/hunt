from typing import Optional
import time
from extract_data.validate import validate_data
from extract_data.get_data_api import fetch_from_api
from extract_data.get_data_browser import fetch_from_browser
from configs.browser_config import BrowserConfig

# ==============================
# Utility Functions
# ==============================
def extract_nested(item, path_list, default=None):
    """Traverse nested dict using path list."""
    value = item
    for key in path_list:
        if isinstance(value, dict):
            value = value.get(key, {})
        else:
            return default
    return value if value not in ({}, None, "") else default

# ==============================
# Filters
# ==============================
def is_active_bounty(item: dict):
    """Check if program is active bounty."""
    return (
        item.get("public", False)
        and not item.get("archived", False)
        and not item.get("disabled", False)
        and item.get("status") == "V"
        and item.get("bounty", False)
        and not item.get("vdp", False)
    )

def normalize_item(item, cfg_fields: dict):
    """Normalize a single item based on config fields."""
    entry = {}
    for field, spec in cfg_fields.items():
        entry[field] = extract_nested(item=item, path_list=spec["path"], default=spec["default"])
    return entry


# ==============================
# Orchestrator Class
# ==============================
class DataExtractor:
    def __init__(self, 
                 config: BrowserConfig, 
                 include_all: bool=False):

        self.config = config
        self.include_all = include_all

    def extract(self) -> list:
        # try with API
        api_data: Optional[list] = self._fetch_all_pages(fetch_from_api)
        if api_data:
            return api_data

        # try with browser
        browser_data: Optional[list] = self._fetch_all_pages(fetch_from_browser)
        if browser_data:
            return browser_data

        # final ERRIR
        return [{"error": "Failed to fetch valid data from both API and browser."}]

    def _fetch_all_pages(self, fetch_func):
        """Loop through all pages using given fetch function."""
        page = 1
        all_items = []

        while True:
            raw_data: Optional[dict] = fetch_func(self.config, page=page)
            if not raw_data or not validate_data(data=raw_data, rules=self.config.validation_rules):
                break

            items: list = raw_data.get("items", [])
            pagination: dict = raw_data.get("pagination", {})

            if not items:
                break

            for item in items:
                if not self.include_all and not is_active_bounty(item):
                    continue
                all_items.append(normalize_item(item=item, cfg_fields=self.config.fields))

            if page >= pagination.get("nb_pages", 1):
                break

            page += 1
            time.sleep(self.config.rate_limit)

        return all_items if all_items else None
