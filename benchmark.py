"""Repeatable index benchmarks, independent of the Streamlit interface."""

import random
import time
import tracemalloc

from DataStructures.trie import Trie
from DataStructures.tst import TST
from data.preprocess import get_words
from search_engine import build_index, search_index

SIZES = [10_000, 50_000, 100_000]


def make_queries(products, count=200, seed=42):
    """Sample title words with replacement, retaining their title frequency."""
    words = [word for product in products for word in get_words(product["title"])]
    return random.Random(seed).choices(words, k=count) if words else []


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


def run_benchmarks(products, sizes=None):
    sizes = SIZES if sizes is None else sizes
    if any(size < 1 or size > len(products) for size in sizes):
        raise ValueError("Every benchmark size must fit the supplied products")
    rows = []
    for size in sizes:
        subset = products[:size]
        queries = make_queries(subset)
        for name, index_class in [("Trie", Trie), ("TST", TST)]:
            index, build_s = measure_build(index_class, subset)
            search_ms = measure_search(index, queries)
            del index
            memory_mb = measure_memory(index_class, subset)
            rows.append(dict(size=size, algorithm=name, build_s=build_s,
                             search_ms=search_ms, memory_mb=memory_mb))
    return rows
