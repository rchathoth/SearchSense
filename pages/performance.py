import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from benchmark import run_benchmarks, supported_sizes
from data.data import PRODUCT_LIMIT, get_products


def benchmark_source_hash():
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for filename in ["DataStructures/trie.py", "DataStructures/tst.py",
                     "search_engine.py", "data/preprocess.py", "data/data.py", "benchmark.py"]:
        digest.update((root / filename).read_bytes())
    return digest.hexdigest()


@st.cache_data(persist="disk", show_spinner="Running benchmarks...")
def get_benchmarks(source_hash, dataset_hash, _products):
    return pd.DataFrame(run_benchmarks(_products))


st.title("Algorithm Performance Comparison")
products = get_products()
sizes = supported_sizes(products)
st.caption(f"Comparing {len(products):,} product titles. Results are medians of three runs; queries mix words, prefixes, and multiword titles.")
if not sizes:
    st.info("No products are available for benchmarking.")
    st.stop()
size = st.selectbox("Dataset Size", sizes, index=len(sizes) - 1,
                    format_func=lambda value: f"{value:,} Products")
dataset_hash = hashlib.sha256(json.dumps([p.get("title") for p in products], ensure_ascii=False).encode()).hexdigest()
rows = get_benchmarks(benchmark_source_hash(), dataset_hash, products)
if rows.empty:
    st.info("No searchable product titles are available for benchmarking.")
    st.stop()
selected = rows[rows["size"] == size].set_index("algorithm")

for column, (title, field, unit) in zip(st.columns(3), [
    ("Average Search Time", "search_ms", "ms"),
    ("Index Build Time", "build_s", "s"),
    ("Retained Python Allocations", "memory_mb", "MiB"),
]):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            for metric_column, algorithm in zip(st.columns(2), ["Trie", "TST"]):
                with metric_column:
                    st.caption(algorithm)
                    st.write(f"{selected.loc[algorithm, field]:.3f} {unit}")

for title, field, ylabel in [
    ("Search Time vs Dataset Size", "search_ms", "Average search time (ms)"),
    ("Retained Python Allocations vs Dataset Size", "memory_mb", "Retained Python allocations (MiB)"),
]:
    st.subheader(title)
    fig, ax = plt.subplots(figsize=(8, 4))
    for algorithm in ["Trie", "TST"]:
        values = rows[rows["algorithm"] == algorithm].sort_values("size")
        ax.plot(values["size"], values[field], marker="o", label=algorithm)
    ax.set(xlabel="Dataset size (products)", ylabel=ylabel, xticks=sizes)
    ax.ticklabel_format(axis="x", style="plain")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
