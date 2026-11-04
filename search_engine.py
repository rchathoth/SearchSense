from DataStructures.tst import TST
from data.preprocess import get_words


def build_tst(products: list) -> TST:
    """The product id is the product's index in *products*."""
    tst = TST()
    for i in range(len(products)):
        for word in get_words(products[i]["title"]):
            tst.insert(word, i)
    return tst


def search_tst(tst: TST, query: str) -> list:
    words = get_words(query)
    if len(words) == 0:
        return []

    # Every query word is a prefix, and a product has to match all of them.
    matches = set(tst.prefix_search(words[0]))
    for word in words[1:]:
        matches = matches & set(tst.prefix_search(word))

    return sorted(matches)
