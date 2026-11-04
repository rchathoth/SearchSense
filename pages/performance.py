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


st.title("Algorithm Performance Comparison", anchor=False)
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
    ("Memory Usage", "memory_mb", "MB"),
]):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            for metric_column, algorithm in zip(st.columns(2), ["Trie", "TST"]):
                with metric_column:
                    st.caption(algorithm)
                    st.write(f"{selected.loc[algorithm, field]:.3f} {unit}")

CHARTS = [
    ("Search Time", "search_ms", "Search Time (ms)",
     "How long one search takes on average, in milliseconds. Each structure runs the same "
     "200 test searches (whole words, partial words and two-word phrases) at every dataset size. "
     "Lower is faster."),
    ("Memory Usage", "memory_mb", "Memory Usage (MB)",
     "How much memory the structure takes up after every product title has been added to it, "
     "in megabytes. Lower means it uses less memory."),
]
LINE_COLORS = {"Trie": "#1f77b4", "TST": "#d62728"}

size_labels = []
for value in sizes:
    size_labels.append(f"{value // 1000}K")

for column, (title, field, ylabel, explanation) in zip(st.columns(2), CHARTS):
    with column:
        st.subheader(title, anchor=False)
        fig, ax = plt.subplots(figsize=(5, 3.5))
        for algorithm in ["Trie", "TST"]:
            values = rows[rows["algorithm"] == algorithm].sort_values("size")
            ax.plot(values["size"], values[field], marker="o", label=algorithm,
                    color=LINE_COLORS[algorithm])
        ax.set(xlabel="Dataset Size (products)", ylabel=ylabel)
        ax.set_xticks(sizes, size_labels)
        ax.set_ylim(bottom=0)
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(explanation)
