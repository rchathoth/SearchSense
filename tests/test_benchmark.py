from benchmark import make_queries, run_benchmarks

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
    assert set(queries) <= {"blue", "summer", "dress", "cotton", "shirt", "hat"}
    assert make_queries([{"title": None}]) == []


def test_benchmark_rows():
    rows = run_benchmarks(PRODUCTS, sizes=[2, 4])
    assert [(row["size"], row["algorithm"]) for row in rows] == [
        (2, "Trie"), (2, "TST"), (4, "Trie"), (4, "TST")]
    for row in rows:
        assert set(row) == {"size", "algorithm", "build_s", "search_ms", "memory_mb"}
        assert all(row[key] > 0 for key in ["build_s", "search_ms", "memory_mb"])
