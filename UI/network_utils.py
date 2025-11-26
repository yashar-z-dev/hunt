def split_message(text: str, max_length: int = 4096) -> list[str]:
    lines = text.split("\n")
    current_message = ""
    messages = []

    for line in lines:
        if len(current_message) + len(line) + 1 <= max_length:
            current_message += ("\n" + line) if current_message else line
        else:
            messages.append(current_message)
            current_message = line

    if current_message:
        messages.append(current_message)

    return messages