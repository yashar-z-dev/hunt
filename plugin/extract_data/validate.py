import json
import os
import datetime

def validate_data(data, rules, debug_log_dir="logs"):
    """
    Validate that required keys exist in data.
    Supports nested keys with dot notation (e.g. 'items.title').
    Logs errors into a file instead of printing.
    """
    if not isinstance(data, dict):
        _log_invalid_data(data, "Data is not a dictionary", None, debug_log_dir)
        return False

    for rule in rules:
        path = rule.get("key")
        keys = path.split(".")

        # Traverse path
        value = data
        for i, key in enumerate(keys):
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                # If we hit a list, check each element
                for idx, element in enumerate(value):
                    sub_path = ".".join(keys[i+1:])
                    sub_rule = {"key": sub_path}
                    if not validate_data(element, [sub_rule], debug_log_dir):
                        _log_invalid_data(
                            element,
                            f"Missing key '{sub_path}' in list element.",
                            idx,
                            debug_log_dir
                        )
                        return False
                value = None  # handled by recursion
                break
            else:
                value = None
                break

        # Final check
        if value is None or value == {} or value == "":
            _log_invalid_data(
                data,
                f"Missing key '{path}'.",
                None,
                debug_log_dir
            )
            return False

    return True


def _log_invalid_data(data, message, item_index, debug_log_dir):
    """Helper to log invalid data into a file for debugging."""
    os.makedirs(debug_log_dir, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(debug_log_dir, f"invalid_data_{timestamp}.json")

    log_entry = {
        "error": message,
        "item_index": item_index,
        "data": data
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)
