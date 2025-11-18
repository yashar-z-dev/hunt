import difflib

def diff_to_dict(first: str, second: str) -> dict:
    """
    مقایسه دو رشته خط به خط و برگرداندن نتیجه در قالب دیکشنری
    شامل سه کلید: removed, added, common
    """
    lines_first = first.strip().splitlines()
    lines_second = second.strip().splitlines()

    diff = difflib.ndiff(lines_first, lines_second)

    result = {
        "removed": [],
        "added": [],
        "common": []
    }

    for line in diff:
        flag, content = line[0], line[2:]
        if flag == "-":
            result["removed"].append(content)
        elif flag == "+":
            result["added"].append(content)
        elif flag == " ":
            result["common"].append(content)

    return result

def build_message_custom(user: dict, message: dict) -> str:
    """تولید پیام شخصی‌سازی‌شده برای یک کاربر"""
    if user["removed"] == 0 and user["added"] == 0 and user["common"] == 0:
        return "hidden"

    mapping = {
        "removed": {"icon": "🔴", "label": "removed"},
        "added": {"icon": "🟢", "label": "added"},
        "common": {"icon": "🔵", "label": "common"}
    }

    output_lines = []
    for key in ["removed", "added", "common"]:
        if user[key] == 1:
            icon = mapping[key]["icon"]
            label = mapping[key]["label"]
            output_lines.append(f"{icon} {label}:")
            output_lines.append(message[key])

    return "\n".join(output_lines)