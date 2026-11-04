from data.preprocess import get_words


def build_index(index, products: list):
    """Works with a Trie or a TST. The product id is the product's index in *products*."""
    for i in range(len(products)):
        for word in get_words(products[i]["title"]):
            index.insert(word, i)
    return index


def search_index(index, query: str) -> list:
    words = get_words(query)
    if len(words) == 0:
        return []

    # Every query word is a prefix, and a product has to match all of them.
    matches = set(index.prefix_search(words[0]))
    for word in words[1:]:
        matches = matches & set(index.prefix_search(word))

    return sorted(matches)


def get_suggestions(index, text: str, k: int) -> list:
    words = get_words(text)
    if len(words) == 0:
        return []

    if len(words) == 1:
        return index.autocomplete(words[0], k)

    start = " ".join(words[:-1])
    start_matches = set(search_index(index, start))

    phrases = []
    for word in index.autocomplete(words[-1], 50):
        count = len(start_matches & set(index.get_product_ids(word)))

        # Skip phrases that wouldn't find any products.
        if count > 0:
            phrases.append((start + " " + word, count))

    phrases.sort(key=lambda pair: pair[1], reverse=True)

    suggestions = []
    for phrase, count in phrases[:k]:
        suggestions.append(phrase)
    return suggestions
