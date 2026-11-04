from benchmark import make_queries, run_benchmarks, supported_sizes

PRODUCTS = [
    {"title": "Blue summer dress"},
    {"title": "Blue cotton shirt"},
    {"title": "Summer hat"},
    {"title": None},
]


def test_queries_are_deterministic():
    queries = make_queries(PRODUCTS)
    assert queries == make_queries(PRODUCTS)
    assert len(queries) == 200
    assert any(" " in query for query in queries)
    assert any(query in {"bl", "sum", "dre", "cot", "sh", "h"} for query in queries)
    assert make_queries([{"title": None}]) == []


def test_benchmark_rows():
    rows = run_benchmarks(PRODUCTS, sizes=[2, 4])
    assert [(row["size"], row["algorithm"]) for row in rows] == [
        (2, "Trie"), (2, "TST"), (4, "Trie"), (4, "TST")]
    for row in rows:
        assert set(row) == {"size", "algorithm", "build_s", "search_ms", "memory_mb"}
        assert all(row[key] > 0 for key in ["build_s", "search_ms", "memory_mb"])


def test_short_and_empty_datasets():
    assert supported_sizes([]) == []
    assert supported_sizes(PRODUCTS) == [4]
    assert run_benchmarks([]) == []
    assert run_benchmarks([{"title": None}]) == []
