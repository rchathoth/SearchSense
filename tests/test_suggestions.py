from DataStructures.trie import Trie
from DataStructures.tst import TST
from search_engine import build_index, get_suggestions


PRODUCTS = [
    {"title": "Wireless Headphones"},
    {"title": "Wireless Headset"},
    {"title": "Cotton Headband"},
    {"title": "Summer Dress"},
    {"title": "Summer Dresses Pack"},
    {"title": "Party Dress"},
    {"title": "Dream Catcher Earrings"},
]


def test_single_word():
    tst = build_index(TST(), PRODUCTS)
    assert get_suggestions(tst, "dre", 5) == ["dress", "dream", "dresses"]
    assert get_suggestions(tst, "DRE", 5) == ["dress", "dream", "dresses"]


def test_phrase_keeps_first_words():
    tst = build_index(TST(), PRODUCTS)
    assert get_suggestions(tst, "wireless head", 5) == ["wireless headphones", "wireless headset"]


def test_phrases_ranked_by_matching_products():
    tst = build_index(TST(), PRODUCTS)
    assert get_suggestions(tst, "summer d", 5) == ["summer dress", "summer dresses"]


def test_dead_phrases_are_skipped():
    tst = build_index(TST(), PRODUCTS)
    assert "wireless headband" not in get_suggestions(tst, "wireless head", 5)


def test_k_limit():
    tst = build_index(TST(), PRODUCTS)
    assert get_suggestions(tst, "dre", 1) == ["dress"]


def test_no_suggestions():
    tst = build_index(TST(), PRODUCTS)
    assert get_suggestions(tst, "", 5) == []
    assert get_suggestions(tst, "   ", 5) == []
    assert get_suggestions(tst, "zzz", 5) == []


def test_trie_matches_tst():
    trie = build_index(Trie(), PRODUCTS)
    tst = build_index(TST(), PRODUCTS)
    for text in ["dre", "wireless head", "summer d", "c", "zzz"]:
        assert get_suggestions(trie, text, 5) == get_suggestions(tst, text, 5)


if __name__ == "__main__":
    test_single_word()
    test_phrase_keeps_first_words()
    test_phrases_ranked_by_matching_products()
    test_dead_phrases_are_skipped()
    test_k_limit()
    test_no_suggestions()
    test_trie_matches_tst()
    print("all tests passed")
