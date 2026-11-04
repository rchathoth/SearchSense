import html
import time
from pathlib import Path

import streamlit as st
from streamlit_searchbox import st_searchbox

from data.data import load_fashion_products
from DataStructures.trie import Trie
from DataStructures.tst import TST
from search_engine import build_index, get_suggestions, search_index


DISPLAY_LIMIT = 21
GRID_COLUMNS = 3

# The suggestion menu is the div right after the box, so "& + div" styles it.
# This makes the box and the menu look like one piece with no gap in between.
SEARCHBOX_STYLE = {
    "dropdown": {"width": 0, "height": 0},
    "searchbox": {
        "optionEmpty": "hidden",
        "control": {
            "minHeight": "40px",
            "backgroundColor": "#ffffff",
            "border": "1px solid #d5d9d9",
            "borderRadius": "12px",
            "boxShadow": "none",
            "&:hover": {"border": "1px solid #d5d9d9"},
            "&:focus-within": {"border": "1px solid #c45500"},
            "&:has(+ div [id*='-option-'])": {"borderBottomLeftRadius": 0, "borderBottomRightRadius": 0},
            "& + div:not(:has([id*='-option-']))": {"display": "none"},
            "& + div": {
                "marginTop": 0,
                "border": "1px solid #c45500",
                "borderTop": "none",
                "borderRadius": "0 0 12px 12px",
                "boxShadow": "none",
                "overflow": "hidden",
            },
        },
        "menuList": {"paddingTop": 0, "paddingBottom": 0},
        "option": {"&:hover": {"backgroundColor": "#f5f5f5"}},
    },
}


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
    return build_index(TST(), get_products())


@st.cache_resource(show_spinner="Building Trie index...")
def get_trie():
    return build_index(Trie(), get_products())


def get_selected_index():
    if st.session_state.get("algorithm") == "Ternary Search Tree":
        return get_tst()
    return get_trie()


def suggest(text: str) -> list:
    return get_suggestions(get_selected_index(), text, 5)


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
query_col, button_col = st.columns([5, 1], vertical_alignment="top")
with query_col:
    query = st_searchbox(
        suggest,
        placeholder="Search products...",
        key="query",
        default_use_searchterm=True,
        edit_after_submit="current",
        style_overrides=SEARCHBOX_STYLE,
    )
with button_col:
    st.button("Search", type="primary", width="stretch")

# 3. Algorithm select
st.radio("Search Algorithm", ["Trie (Prefix Tree)", "Ternary Search Tree"], horizontal=True, key="algorithm")

# 4. Search results
if query is None:
    query = ""

if query.strip() == "":
    results = products
    count_text = f"Showing {DISPLAY_LIMIT} of {len(products):,} Products"
    time_text = "Search Time: 0 ms"
else:
    index = get_selected_index()

    start = time.perf_counter()
    result_ids = search_index(index, query)
    search_ms = (time.perf_counter() - start) * 1000

    results = []
    for product_id in result_ids:
        results.append(products[product_id])
    count_text = f"{len(results):,} Products Found"
    time_text = f"Search Time: {search_ms:.2f} ms"

with st.container(border=True):
    count_col, time_col = st.columns(2)
    count_col.text(count_text)
    time_col.text(time_text)

    if query.strip() != "" and len(results) == 0:
        st.text("No products found")

    shown = results[:DISPLAY_LIMIT]
    for row_start in range(0, len(shown), GRID_COLUMNS):
        row = shown[row_start:row_start + GRID_COLUMNS]
        for column, product in zip(st.columns(GRID_COLUMNS), row):
            with column:
                render_product(product)
