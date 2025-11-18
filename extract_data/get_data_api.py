import requests
import time

def fetch_from_api(config, page=1):
    """
    Fetch one page from API with retries, exponential backoff, and detailed error info.
    """
    backoff = config["retry_delay"]
    for attempt in range(1, config["max_retries"] + 1):
        try:
            response = requests.get(
                f"{config['base_url']}&page[number]={page}",
                timeout=config["timeout"]
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout on page {page}, attempt {attempt}: {e}"
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error on page {page}, attempt {attempt}: {e}"
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error on page {page}, attempt {attempt}: {e}"
        except Exception as e:
            error_msg = f"Unexpected error on page {page}, attempt {attempt}: {e}"

        # اگر هنوز فرصت retry داریم
        if attempt < config["max_retries"]:
            time.sleep(backoff)
            backoff *= 2  # backoff تصاعدی
        else:
            return {
                "error": "API fetch failed",
                "page": page,
                "attempts": attempt,
                "details": error_msg
            }
