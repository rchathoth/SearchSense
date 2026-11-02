import streamlit as st

from data.data import PRODUCT_LIMIT


ALGORITHMS = ["Trie (Prefix Tree)", "Ternary Search Tree"]
METRICS = ["Build time", "Avg. search time", "Memory used", "Node count"]

# Benchmark numbers per algorithm, keyed by metric name; anything missing shows as "—"
results = {name: {} for name in ALGORITHMS}


def render_algorithm_card(name: str, stats: dict) -> None:
    with st.container(border=True):
        st.subheader(name)
        for row_start in range(0, len(METRICS), 2):
            for column, metric in zip(st.columns(2), METRICS[row_start:row_start + 2]):
                column.metric(metric, stats.get(metric, "—"))


st.title("Algorithm Performance Comparison")
st.caption(f"How the two prefix structures compare on the same {PRODUCT_LIMIT:,} product titles")

for column, name in zip(st.columns(2), ALGORITHMS):
    with column:
        render_algorithm_card(name, results[name])

st.subheader("Search time by prefix length")
with st.container(border=True, height=300, vertical_alignment="center"):
    st.caption("Chart appears here once the benchmarks run", text_alignment="center")
