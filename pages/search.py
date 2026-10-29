import streamlit as st

from data.data import load_fashion_products


DISPLAY_LIMIT = 20


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


def format_price(price) -> str:
    if price is None:
        return "Price unavailable"
    return f"${float(price):.2f}"


def format_rating(product: dict) -> str:
    if product["average_rating"] is None:
        return "No ratings"
    return f"Rating: {product['average_rating']} ({product['rating_number'] or 0:,} ratings)"


def render_product(product: dict) -> None:
    with st.container(border=True):
        image_col, info_col, button_col = st.columns([1, 4, 1])

        with image_col:
            if product["image"]:
                st.image(product["image"])
            else:
                st.text("No image")

        with info_col:
            st.markdown(f"**{product['title']}**")
            st.text(format_rating(product))
            st.text(format_price(product["price"]))
            st.caption(product["main_category"] or "")

        with button_col:
            st.button("View Details", key=f"details-{product['parent_asin']}")


products = get_products()

# 1. Heading
st.title("Find Your Next Favorite Product")
st.caption(f"Search through {len(products):,} Amazon products")

# 2. Search bar + autocomplete
query_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
with query_col:
    st.text_input("Search", placeholder="Search products...", label_visibility="collapsed")
with button_col:
    st.button("Search", use_container_width=True)
suggestions = st.empty()

# 3. Algorithm select
st.radio("Search Algorithm", ["Trie (Prefix Tree)", "Ternary Search Tree"], horizontal=True)

# 4. Search results
with st.container(border=True):
    count_col, time_col = st.columns(2)
    count_col.text(f"Showing {DISPLAY_LIMIT} of {len(products):,} Products")
    time_col.text("Search Time: 0 ms")

    for product in products[:DISPLAY_LIMIT]:
        render_product(product)
