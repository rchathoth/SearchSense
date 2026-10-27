from datasets import load_dataset


DATASET_NAME = "McAuley-Lab/Amazon-Reviews-2023"
DATASET_CONFIG = "raw_meta_Amazon_Fashion"
PRODUCT_LIMIT = 100_000


def load_fashion_products(limit: int = PRODUCT_LIMIT) -> list[dict]:
    if not 1 <= limit <= PRODUCT_LIMIT:
        raise ValueError(f"limit must be between 1 and {PRODUCT_LIMIT}")

    products = []
    seen_ids = set()

    dataset = load_dataset(
        DATASET_NAME,
        DATASET_CONFIG,
        split="full",
        streaming=True,
    )

    for product in dataset:
        product_id = product.get("parent_asin") or product.get("asin")
        if product_id is None or product_id in seen_ids:
            continue

        seen_ids.add(product_id)
        products.append(product)
        if len(products) == limit:
            break

    return products
