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
