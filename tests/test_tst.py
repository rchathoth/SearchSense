from DataStructures.tst import TST
from data.preprocess import get_words
from search_engine import build_tst, search_tst


def make_tst():
    tst = TST()
    tst.insert("wire", 0)
    tst.insert("wireless", 0)
    tst.insert("wireless", 1)
    tst.insert("wireless", 2)
    tst.insert("wig", 3)
    tst.insert("dress", 4)
    return tst


def test_search():
    tst = make_tst()
    assert tst.search("wire")
    assert tst.search("wireless")
    assert not tst.search("wir")
    assert not tst.search("hat")


def test_product_ids():
    tst = TST()
    tst.insert("dress", 5)
    tst.insert("dress", 5)
    tst.insert("dress", 7)
    assert tst._find_node("dress").product_ids == [5, 7]


def test_prefix_search():
    tst = make_tst()
    assert sorted(tst.prefix_search("wire")) == [0, 1, 2]
    assert sorted(tst.prefix_search("wi")) == [0, 1, 2, 3]
    assert tst.prefix_search("dress") == [4]
    assert tst.prefix_search("hat") == []
    assert tst.prefix_search("") == []


def test_autocomplete():
    tst = make_tst()
    assert tst.autocomplete("wi", 5) == ["wireless", "wig", "wire"]
    assert tst.autocomplete("wi", 1) == ["wireless"]
    assert tst.autocomplete("x", 5) == []
    assert tst.autocomplete("", 5) == []


def test_delete():
    tst = make_tst()
    tst.delete("wireless")
    assert not tst.search("wireless")
    assert tst.search("wire")
    assert sorted(tst.prefix_search("wire")) == [0]


def test_get_words():
    assert get_words("Men's Running Shoes, Running!") == ["men", "s", "running", "shoes"]
    assert get_words("") == []
    assert get_words(None) == []


def test_search_tst():
    products = [
        {"title": "Wireless Headphones"},
        {"title": "Wireless Mouse"},
        {"title": "Summer Dress"},
        {"title": None},
    ]
    tst = build_tst(products)
    assert search_tst(tst, "wireless") == [0, 1]
    assert search_tst(tst, "wire head") == [0]
    assert search_tst(tst, "DRESS!") == [2]
    assert search_tst(tst, "hat") == []
    assert search_tst(tst, "   ") == []


if __name__ == "__main__":
    test_search()
    test_product_ids()
    test_prefix_search()
    test_autocomplete()
    test_delete()
    test_get_words()
    test_search_tst()
    print("all tests passed")
