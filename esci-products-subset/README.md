# Shopping Queries (ESCI), a Product Search Subset

A small product search benchmark cut from Amazon's Shopping Queries Dataset: 20,027
products of the US store, 150 real customer queries, and 3,728 human relevance
judgments, labelled E (Exact), S (Substitute), C (Complement) or I (Irrelevant).

## Files

- `products.parquet`: `product_id`, `title`, `brand`, `color`, `bullets` (the bullet
  points), `description` (both stripped of HTML and cut at 600 characters).
- `queries.parquet`: `query_id`, `query`.
- `qrels.parquet`: `query_id`, `product_id`, `esci_label`.
- `build.py`: the script that built the subset (its docstring says how and what was
  chosen). A product with no judgment for a query counts as irrelevant to it.
- `lab-results/`: what the product search lab computes on a GPU (Colab's image on an RTX
  A4000), which it loads when it runs without one. `product-embeddings.npy` (float16,
  (20027, 1024), `products.parquet`'s order) and `query-embeddings.npy` (float16, (150,
  1024), `queries.parquet`'s order): `Qwen/Qwen3-Embedding-0.6B` in float16,
  `max_seq_length` 128, `encode_document` on `title + ". " + brand + ". " + bullets`,
  `encode_query` on the queries. `reranked.parquet` (`query_id`, `rank`, `product_id`):
  for the first 100 queries, their 100 hybrid results (BM25 and dense, fused by RRF) with
  the first 50 reranked by `BAAI/bge-reranker-v2-m3` in float16 (`max_length` 512).

## Source

Reddy et al., *Shopping Queries Dataset: A Large-Scale ESCI Benchmark for Improving
Product Search* (2022), https://github.com/amazon-science/esci-data

## License

Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0), Amazon.com, Inc.
