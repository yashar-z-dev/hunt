import time
from typing import Optional
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
                 include_all: bool=False) -> Optional[list]:

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
        return None

    def _fetch_all_pages(self, fetch_func) -> Optional[list]:
        """
        Fetch and normalize items across all pages using the given fetch function.
        - Stops if data is invalid, empty, or no more pages.
        - Respects rate limit between requests.
        """
        all_items = []
        page = 1

        while True:
            raw_data: Optional[dict] = fetch_func(self.config, page=page)
            if not raw_data or not validate_data(data=raw_data, rules=self.config.validation_rules):
                break

            items = raw_data.get("items") or []
            if not items:
                break

            # Process items
            for item in items:
                if self.include_all or is_active_bounty(item):
                    all_items.append(normalize_item(item, self.config.fields))

            # Pagination check
            nb_pages = raw_data.get("pagination", {}).get("nb_pages", 1)
            if page >= nb_pages:
                break

            page += 1
            time.sleep(self.config.rate_limit)

        return all_items or None
