import streamlit as st


st.set_page_config(page_title="SearchSense", layout="centered")

search_page = st.Page("pages/search.py", title="Search", default=True)
performance_page = st.Page("pages/performance.py", title="Performance")

page = st.navigation([search_page, performance_page], position="top")
page.run()
