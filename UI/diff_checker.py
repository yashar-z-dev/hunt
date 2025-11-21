import difflib

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

                for j in message[item["key"]]:
                    output_lines.append(j)
            
    if output_lines:
        return "\n".join(output_lines)
    else:
        return "__NOT_CHANGE__"

if __name__ == "__main__":
    flags = input(">> ")
    with open("file_1", "r", encoding="utf-8") as f:
        data_1 = f.read()
    with open("file_2", "r", encoding="utf-8") as f:
        data_2 = f.read()
    result = diff_to_dict(first=data_1, second=data_2)
    output = build_message_custom(user_data=flags, message=result)
    print(output)