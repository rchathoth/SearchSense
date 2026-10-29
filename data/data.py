import json
import ssl
import urllib.request

import certifi


DATASET_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023"
    "/resolve/main/raw/meta_categories/meta_Amazon_Fashion.jsonl"
)
PRODUCT_LIMIT = 100_000


def load_fashion_products(limit: int = PRODUCT_LIMIT) -> list[dict]:
    """Stream the first `limit` unique products from the Amazon Fashion metadata."""
    if not 1 <= limit <= PRODUCT_LIMIT:
        raise ValueError(f"limit must be between 1 and {PRODUCT_LIMIT}")

    products = []
    seen_ids = set()

    # python.org builds of Python on macOS ship without CA certs, so use certifi's
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(DATASET_URL, context=context) as response:
        for line in response:
            product = json.loads(line)

            product_id = product.get("parent_asin") or product.get("asin")
            if product_id is None or product_id in seen_ids:
                continue

            seen_ids.add(product_id)
            products.append(product)
            if len(products) == limit:
                break

    return products
