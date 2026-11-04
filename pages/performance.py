import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from benchmark import SIZES, run_benchmarks
from data.data import PRODUCT_LIMIT, get_products


def benchmark_source_hash():
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for filename in ["DataStructures/trie.py", "DataStructures/tst.py",
                     "search_engine.py", "data/preprocess.py", "benchmark.py"]:
        digest.update((root / filename).read_bytes())
    return digest.hexdigest()


@st.cache_data(persist="disk", show_spinner="Running benchmarks...")
def get_benchmarks(source_hash):
    return pd.DataFrame(run_benchmarks(get_products()))


st.title("Algorithm Performance Comparison")
st.caption(f"How the two prefix structures compare on the same {PRODUCT_LIMIT:,} product titles")

size = st.selectbox("Dataset Size", SIZES, index=2,
                    format_func=lambda value: f"{value:,} Products")
rows = get_benchmarks(benchmark_source_hash())
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

for title, field, ylabel in [
    ("Search Time vs Dataset Size", "search_ms", "Average search time (ms)"),
    ("Memory Usage vs Dataset Size", "memory_mb", "Memory usage (MB)"),
]:
    st.subheader(title)
    fig, ax = plt.subplots(figsize=(8, 4))
    for algorithm in ["Trie", "TST"]:
        values = rows[rows["algorithm"] == algorithm].sort_values("size")
        ax.plot(values["size"], values[field], marker="o", label=algorithm)
    ax.set(xlabel="Dataset size (products)", ylabel=ylabel, xticks=SIZES)
    ax.ticklabel_format(axis="x", style="plain")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
