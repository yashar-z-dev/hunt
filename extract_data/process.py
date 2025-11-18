import json
import time
from extract_data.validate import validate_data
from extract_data.get_data_api import fetch_from_api
from extract_data.get_data_browser import fetch_from_browser

# ==============================
# Config (can be externalized)
# ==============================
CONFIG = {
    "base_url": "https://api.yeswehack.com/programs?filter%5Btype%5D%5B%5D=bug-bounty",
    "timeout": 15,
    "max_retries": 3,
    "retry_delay": 5,
    "fields": {
        "title": {"path": ["title"], "default": "N/A"},
        "business_unit": {"path": ["business_unit", "name"], "default": "N/A"},
        "last_update_at": {"path": ["last_update_at"], "default": None},
    },
    "validation_rules": [
        {"key": "items"},  # dataset must contain "items"
    ],
}

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
def is_active_bounty(item):
    """Check if program is active bounty."""
    return (
        item.get("public", False)
        and not item.get("archived", False)
        and not item.get("disabled", False)
        and item.get("status") == "V"
        and item.get("bounty", False)
        and not item.get("vdp", False)
    )

def normalize_item(item, config):
    """Normalize a single item based on config fields."""
    entry = {}
    for field, spec in config["fields"].items():
        entry[field] = extract_nested(item, spec["path"], spec["default"])
    return entry


# ==============================
# Orchestrator Class
# ==============================
class DataExtractor:
    def __init__(self, config=CONFIG, include_all=False):
        self.config = config
        self.include_all = include_all

    def extract(self):
        # try with API
        api_data = self._fetch_all_pages(fetch_from_api)
        if api_data:
            return api_data

        # try with browser
        browser_data = self._fetch_all_pages(fetch_from_browser)
        if browser_data:
            return browser_data

        # final ERRIR
        return {"error": "Failed to fetch valid data from both API and browser."}

    def _fetch_all_pages(self, fetch_func):
        """Loop through all pages using given fetch function."""
        page = 1
        all_items = []

        while True:
            raw_data = fetch_func(self.config, page=page)
            if not raw_data or not validate_data(raw_data, self.config["validation_rules"]):
                break

            items = raw_data.get("items", [])
            pagination = raw_data.get("pagination", {})

            if not items:
                break

            for item in items:
                if not self.include_all and not is_active_bounty(item):
                    continue
                all_items.append(normalize_item(item, self.config))

            if page >= pagination.get("nb_pages", 1):
                break

            page += 1
            time.sleep(1)  # rate limit

        return all_items if all_items else None
