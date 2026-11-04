import html
import time
from pathlib import Path

import streamlit as st

from data.data import load_fashion_products
from data.preprocess import get_words
from search_engine import build_tst, search_tst


DISPLAY_LIMIT = 21
GRID_COLUMNS = 3


@st.cache_data(persist="disk", show_spinner="Loading products...")
def get_products() -> list[dict]:
    """Load the dataset once and keep only the fields the UI needs."""
    products = []
    for product in load_fashion_products():
        images = product.get("images") or []
        image = next((img.get("large") for img in images if img.get("large")), None)

        products.append({
            "parent_asin": product.get("parent_asin") or product.get("asin"),
            "title": product.get("title"),
            "main_category": product.get("main_category"),
            "price": product.get("price"),
            "average_rating": product.get("average_rating"),
            "rating_number": product.get("rating_number"),
            "image": image,
        })
    return products


@st.cache_resource(show_spinner="Building TST index...")
def get_tst():
    return build_tst(get_products())


def format_rating(product: dict) -> str:
    # Always two lines (stars, then count) so cards in a row stay the same height
    rating = product["average_rating"]
    if rating is None:
        return ":gray[☆☆☆☆☆]  \n:small[No ratings yet]"

    filled = int(rating + 0.5)
    stars = "★" * filled + "☆" * (5 - filled)
    count = product["rating_number"] or 0
    noun = "rating" if count == 1 else "ratings"
    return f":orange[{stars}] {rating}  \n:small[{count:,} {noun}]"


def render_product(product: dict) -> None:
    with st.container(border=True, key=f"card-{product['parent_asin']}"):
        if product["image"]:
            st.html(f'<div class="product-image"><img src="{html.escape(product["image"])}" alt=""></div>')
        else:
            st.html('<div class="product-image product-image--empty">No image</div>')

        # st.html instead of st.markdown so "$" or "*" in a title isn't parsed as LaTeX/markdown
        st.html(f'<div class="product-title">{html.escape(product["title"] or "Untitled")}</div>')
        st.markdown(format_rating(product))

        if product["price"] is None:
            st.markdown(":gray[No price listed]")
        else:
            st.markdown(f"**\\${float(product['price']):.2f}**")

        st.caption(product["main_category"] or "")
        st.button("View Details", key=f"details-{product['parent_asin']}", width="stretch")


st.html(Path("assets/styles.css"))
products = get_products()

# 1. Heading
st.title("Find Your Next Favorite Product")
st.caption(f"Search through {len(products):,} Amazon products")

# 2. Search bar + autocomplete
query_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
with query_col:
    query = st.text_input(
        "Search",
        placeholder="Search products...",
        label_visibility="collapsed",
        icon=":material/search:",
    )
with button_col:
    st.button("Search", type="primary", width="stretch")
suggestions = st.empty()

# 3. Algorithm select
algorithm = st.radio("Search Algorithm", ["Trie (Prefix Tree)", "Ternary Search Tree"], horizontal=True)

# 4. Search results
if query.strip() == "":
    results = products
    count_text = f"Showing {DISPLAY_LIMIT} of {len(products):,} Products"
    time_text = "Search Time: 0 ms"
elif algorithm == "Ternary Search Tree":
    tst = get_tst()

    start = time.perf_counter()
    result_ids = search_tst(tst, query)
    search_ms = (time.perf_counter() - start) * 1000

    results = []
    for product_id in result_ids:
        results.append(products[product_id])
    count_text = f"{len(results):,} Products Found"
    time_text = f"Search Time: {search_ms:.2f} ms"

    words = get_words(query)
    if len(words) > 0:
        suggestions_list = tst.autocomplete(words[-1], 5)
        if len(suggestions_list) > 0:
            suggestions.caption("Suggestions: " + ", ".join(suggestions_list))
else:
    results = []
    count_text = "Trie search isn't hooked up yet"
    time_text = "Search Time: 0 ms"

with st.container(border=True):
    count_col, time_col = st.columns(2)
    count_col.text(count_text)
    time_col.text(time_text)

    if query.strip() != "" and len(results) == 0 and algorithm == "Ternary Search Tree":
        st.text("No products found")

    shown = results[:DISPLAY_LIMIT]
    for row_start in range(0, len(shown), GRID_COLUMNS):
        row = shown[row_start:row_start + GRID_COLUMNS]
        for column, product in zip(st.columns(GRID_COLUMNS), row):
            with column:
                render_product(product)
