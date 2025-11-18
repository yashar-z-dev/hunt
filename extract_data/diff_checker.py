import difflib

def diff_to_dict(first: str, second: str) -> dict:
    """return dict with keys: removed, added, common"""
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

def build_message_custom(user_data: str, message: dict) -> str:
    removed = user_data[1] == "1"
    added = user_data[2] == "1"
    common = user_data[3] == "1"

    if not removed and not added and not common:
        return "hidden"

    mapping = {
        "removed": {"icon": "🔴", "label": "removed"},
        "added": {"icon": "🟢", "label": "added"},
        "common": {"icon": "🔵", "label": "common"}
    }

    output_lines = []
    for key in ["removed", "added", "common"]:
        if key:
            icon = mapping[key]["icon"]
            label = mapping[key]["label"]
            output_lines.append(f"{icon} {label}:")
            output_lines.append(message[key])

    if output_lines:
        return "\n".join(output_lines)
    else:
        "__EMPTY__"