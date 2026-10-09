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

## Source

Reddy et al., *Shopping Queries Dataset: A Large-Scale ESCI Benchmark for Improving
Product Search* (2022), https://github.com/amazon-science/esci-data

## License

Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0), Amazon.com, Inc.
