import streamlit as st


st.set_page_config(page_title="SearchSense", page_icon=":material/search:", layout="centered")
st.logo("assets/logo.svg", size="large")

search_page = st.Page("pages/search.py", title="Search", default=True)
performance_page = st.Page("pages/performance.py", title="Performance")

page = st.navigation([search_page, performance_page], position="top")
page.run()

st.divider()
st.caption(
    "Product data from [Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)"
    " by McAuley Lab, UC San Diego",
    text_alignment="center",
)
