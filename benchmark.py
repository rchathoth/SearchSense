"""Repeatable index benchmarks, independent of the Streamlit interface."""

import random
import time
import statistics
import tracemalloc

from DataStructures.trie import Trie
from DataStructures.tst import TST
from data.preprocess import get_words
from search_engine import build_index, search_index

SIZES = [10_000, 50_000, 100_000]


def make_queries(products, count=200, seed=42):
    """Sample reproducible full-word, prefix and multiword queries from titles."""
    titles = [get_words(product.get("title")) for product in products]
    titles = [words for words in titles if words]
    if not titles:
        return []
    rng = random.Random(seed)
    queries = []
    for i in range(count):
        words = rng.choice(titles)
        word = rng.choice(words)
        if i % 3 == 0:
            queries.append(word)
        elif i % 3 == 1:
            queries.append(word[:max(1, len(word) // 2)])
        else:
            queries.append(" ".join(words[:2]))
    return queries


def measure_build(index_class, products):
    """Return the built index and elapsed seconds without memory tracing."""
    start = time.perf_counter()
    index = build_index(index_class(), products)
    return index, time.perf_counter() - start


def measure_memory(index_class, products):
    """Measure retained allocation MiB for an independent index build."""
    tracemalloc.start()
    try:
        index = build_index(index_class(), products)
        current, _ = tracemalloc.get_traced_memory()
        return current / (1024 * 1024)
    finally:
        tracemalloc.stop()


def measure_search(index, queries, rounds=3):
    """Return mean milliseconds per query through the shared search path."""
    if not queries or rounds < 1:
        raise ValueError("Search measurement needs queries and positive rounds")
    start = time.perf_counter()
    for _ in range(rounds):
        for query in queries:
            search_index(index, query)
    return (time.perf_counter() - start) * 1000 / (len(queries) * rounds)


def supported_sizes(products):
    """Include standard sizes that fit, plus the actual size of a short dataset."""
    sizes = [size for size in SIZES if size <= len(products)]
    if products and not sizes:
        sizes.append(len(products))
    return sizes


def run_benchmarks(products, sizes=None, repeats=3):
    sizes = supported_sizes(products) if sizes is None else sizes
    if repeats < 1 or any(size < 1 or size > len(products) for size in sizes):
        raise ValueError("Benchmark sizes must fit the supplied products and repeats must be positive")
    rows = []
    for size in sizes:
        subset = products[:size]
        queries = make_queries(subset)
        if not queries:
            continue
        samples = {name: [] for name in ("Trie", "TST")}
        algorithms = [("Trie", Trie), ("TST", TST)]
        for repeat in range(repeats):
            for name, index_class in algorithms[::1 if repeat % 2 == 0 else -1]:
                index, build_s = measure_build(index_class, subset)
                search_index(index, queries[0])  # Warm the search path.
                search_ms = measure_search(index, queries)
                del index
                memory_mb = measure_memory(index_class, subset)
                samples[name].append((build_s, search_ms, memory_mb))
        for name, _ in algorithms:
            build_s, search_ms, memory_mb = map(statistics.median, zip(*samples[name]))
            rows.append(dict(size=size, algorithm=name, build_s=build_s,
                             search_ms=search_ms, memory_mb=memory_mb))
    return rows
