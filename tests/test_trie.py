from DataStructures.trie import Trie
from DataStructures.tst import TST
from search_engine import build_index, search_index


def make_trie():
    trie = Trie()
    trie.insert("wire", 0)
    trie.insert("wireless", 0)
    trie.insert("wireless", 1)
    trie.insert("wireless", 2)
    trie.insert("wig", 3)
    trie.insert("dress", 4)
    return trie


def test_search():
    trie = make_trie()
    assert trie.search("wire")
    assert trie.search("wireless")
    assert not trie.search("wir")
    assert not trie.search("hat")


def test_product_ids():
    trie = Trie()
    trie.insert("dress", 5)
    trie.insert("dress", 5)
    trie.insert("dress", 7)
    assert trie._find_node("dress").product_ids == [5, 7]


def test_get_product_ids():
    trie = make_trie()
    assert trie.get_product_ids("wireless") == [0, 1, 2]
    assert trie.get_product_ids("wire") == [0]
    assert trie.get_product_ids("wir") == []
    assert trie.get_product_ids("hat") == []
    assert trie.get_product_ids("") == []


def test_prefix_search():
    trie = make_trie()
    assert sorted(trie.prefix_search("wire")) == [0, 1, 2]
    assert sorted(trie.prefix_search("wi")) == [0, 1, 2, 3]
    assert trie.prefix_search("dress") == [4]
    assert trie.prefix_search("hat") == []
    assert trie.prefix_search("") == []


def test_autocomplete():
    trie = make_trie()
    assert trie.autocomplete("wi", 5) == ["wireless", "wig", "wire"]
    assert trie.autocomplete("wi", 1) == ["wireless"]
    assert trie.autocomplete("x", 5) == []
    assert trie.autocomplete("", 5) == []


def test_delete():
    trie = make_trie()
    trie.delete("wireless")
    assert not trie.search("wireless")
    assert trie.search("wire")
    assert sorted(trie.prefix_search("wire")) == [0]


def test_trie_matches_tst():
    products = [
        {"title": "Wireless Headphones"},
        {"title": "Wireless Mouse"},
        {"title": "Summer Dress"},
        {"title": "Dresser Drawer Knobs"},
        {"title": None},
    ]
    trie = build_index(Trie(), products)
    tst = build_index(TST(), products)

    for query in ["wireless", "wire head", "dress", "dr", "DRESS!", "hat", "   "]:
        assert search_index(trie, query) == search_index(tst, query)

    for prefix in ["w", "dr", "s", "zz"]:
        assert trie.autocomplete(prefix, 5) == tst.autocomplete(prefix, 5)


if __name__ == "__main__":
    test_search()
    test_product_ids()
    test_get_product_ids()
    test_prefix_search()
    test_autocomplete()
    test_delete()
    test_trie_matches_tst()
    print("all tests passed")
