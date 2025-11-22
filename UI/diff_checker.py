import difflib
import re

def diff_to_dict(first: str, second: str) -> dict:
    """Return dict with keys: removed, added, common"""
    lines_first = first.strip().splitlines()
    lines_second = second.strip().splitlines()

    diff = difflib.ndiff(lines_first, lines_second)

    result = {
        "removed": [],
        "added": [],
        "common": []
    }

    for line in diff:
        flag, content = line[0], line[2:]  # Check the difference marker and content
        if flag == "-":  # Lines removed from the first string
            result["removed"].append(content)
        elif flag == "+":  # Lines added to the second string
            result["added"].append(content)
        elif flag == " ":  # Lines common to both strings
            result["common"].append(content)

    return result

def truncate(text: str, limit: int = 15) -> str:
    """
    Truncate text to the nearest break at or before `limit`.
    A break is any non-letter (Unicode-aware) or any char in `extra_breaks`.
    If no break exists in the window, hard-cut at `limit`.
    """
    if len(text) <= limit:
        return text

    last_break = -1
    window = text[:limit]

    def is_break(ch: str) -> bool:
        return (not ch.isalpha())

    for i, ch in enumerate(window):
        if is_break(ch):
            last_break = i

    if last_break != -1:
        result = window[:last_break + 1].rstrip()
    else:
        result = window

    return result


def build_message_custom(user_data: str, message: dict) -> str:
    output_lines = []

    if len(user_data) > 3:
        user_data = user_data[-3:]

    mapping = [
        {"key": "removed", "id": 0, "icon": "🔴", "parametr": None},
        {"key": "added",   "id": 1, "icon": "🟢", "parametr": None},
        {"key": "common",  "id": 2, "icon": "🔵", "parametr": None}
        ]

    for idx, item in enumerate(mapping):
        if user_data[item["id"]] == "1":
            if message.get(item["key"], None):
                icon = item["icon"]
                lable = item["key"]
                output_lines.append(f"{icon} {lable}:")

                for data in message[item["key"]]:
                    match = re.match(r'^(.*?),', data)
                    if match:
                        print(match.group(1))
                        result = truncate(text=match.group(1))
                    else:
                        result = truncate(text=f"ERR: {data}")
                    output_lines.append(result)
            
    if output_lines:
        return "\n".join(f"{i}. {item}" for i, item in enumerate(output_lines, start=1))

    else:
        return "__NOT_CHANGE__"