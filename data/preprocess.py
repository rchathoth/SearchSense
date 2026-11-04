def get_words(title: str) -> list:
    if title is None:
        return []

    cleaned = ""
    for char in title.lower():
        if char.isalnum():
            cleaned += char
        elif char == "'":
            # Drop apostrophes so "men's" becomes "mens" instead of "men" and "s".
            continue
        else:
            cleaned += " "

    words = []
    for word in cleaned.split():
        if word not in words:
            words.append(word)
    return words
