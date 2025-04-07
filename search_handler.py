from elasticsearch import Elasticsearch
from collections import defaultdict

es = Elasticsearch("http://localhost:9200")


def get_yearly_sales(year: str):
    index_name = "order_products-logs"

    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31"
                }
            }
        },
        "size": 10000
    }

    res = es.search(index=index_name, body=query)
    sales_summary = defaultdict(int)

    for hit in res['hits']['hits']:
        source = hit["_source"]
        product = source.get("productName")
        quantity = source.get("productQuantity", 0)
        sales_summary[product] += quantity

    return sales_summary
