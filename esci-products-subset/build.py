"""Build the subset from Amazon's Shopping Queries Dataset (run from this directory).

    uv run --no-project --with pandas --with pyarrow python build.py <esci-data dir>

<esci-data dir> holds shopping_queries_dataset_examples.parquet and
shopping_queries_dataset_products.parquet
(https://github.com/amazon-science/esci-data/tree/main/shopping_queries_dataset).

150 English queries of the reduced (`small_version`) test split, each with 3 to 30
Exact products and at least 2 Irrelevant ones among its judgments; the catalog holds
every product judged for them, plus the products judged for other queries of the same
split, as distractors, up to 20,000 products. A distractor isn't judged for the 150
queries: it counts as irrelevant to them, which it almost always is.
"""

import re
import sys
from pathlib import Path

import pandas as pd

source = Path(sys.argv[1])
SEED, N_QUERIES, N_PRODUCTS = 0, 150, 20_000

examples = pd.read_parquet(source / "shopping_queries_dataset_examples.parquet")
examples = examples[(examples.product_locale == "us") & (examples.small_version == 1) & (examples.split == "test")]
counts = examples.groupby("query_id").esci_label.value_counts().unstack(fill_value=0)
eligible = counts[(counts.E.between(3, 30)) & (counts.I >= 2)].index
chosen = pd.Series(eligible).sample(N_QUERIES, random_state=SEED)
qrels = examples[examples.query_id.isin(chosen)][["query_id", "product_id", "esci_label"]]
queries = examples[examples.query_id.isin(chosen)].drop_duplicates("query_id")[["query_id", "query"]]
queries["query"] = queries["query"].str.strip()

others = examples[~examples.query_id.isin(chosen)]
order = pd.Series(others.query_id.unique()).sample(frac=1, random_state=SEED)
catalog_ids = set(qrels.product_id)
pools = others.groupby("query_id").product_id.apply(list)
for query_id in order:
    if len(catalog_ids) >= N_PRODUCTS:
        break
    catalog_ids.update(pools[query_id])

products = pd.read_parquet(source / "shopping_queries_dataset_products.parquet")
products = products[(products.product_locale == "us") & products.product_id.isin(catalog_ids)]
tags = re.compile(r"<[^>]+>")


def clean(text: object, limit: int) -> str:
    text = " ".join(tags.sub(" ", text).split()) if isinstance(text, str) else ""
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


products = pd.DataFrame({
    "product_id": products.product_id,
    "title": products.product_title.map(lambda t: clean(t, 300)),
    "brand": products.product_brand.fillna(""),
    "color": products.product_color.fillna(""),
    "bullets": products.product_bullet_point.map(lambda t: clean(t, 600)),
    "description": products.product_description.map(lambda t: clean(t, 600)),
}).reset_index(drop=True)
qrels = qrels[qrels.product_id.isin(products.product_id)]
products.to_parquet("products.parquet", index=False)
queries.sort_values("query_id").to_parquet("queries.parquet", index=False)
qrels.sort_values(["query_id", "product_id"]).to_parquet("qrels.parquet", index=False)
print(len(products), "products,", len(queries), "queries,", len(qrels), "judgments")
print(qrels.esci_label.value_counts().to_dict())
print(queries.sample(15, random_state=1)["query"].tolist())
