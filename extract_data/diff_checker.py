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
    removed = user_data[1] == "1"
    added = user_data[2] == "1"
    common = user_data[3] == "1"

    if not removed and not added and not common:
        return "hidden"  # Return "hidden" if no relevant changes

    mapping = {
        "removed": {"icon": "🔴", "label": "removed"},
        "added": {"icon": "🟢", "label": "added"},
        "common": {"icon": "🔵", "label": "common"}
    }

    output_lines = []
    
    # For each key in the mapping (removed, added, common), process and generate message
    for key in ["removed", "added", "common"]:
        if key and message[key]:  # Only process if the key has any content
            icon = mapping[key]["icon"]
            label = mapping[key]["label"]
            
            # Add the icon and label to output
            output_lines.append(f"{icon} {label}:")

            # Add the actual lines (added, removed, common) for that key
            for item in message[key]:
                output_lines.append(item)
            
            output_lines.append("")  # Add a blank line for separation

    if output_lines:
        return "\n".join(output_lines)  # Join all the output lines into a single string
    else:
        return "__EMPTY__"  # Return "__EMPTY__" if no changes
