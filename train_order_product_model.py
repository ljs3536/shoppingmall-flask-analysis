import pandas as pd
import pickle
import os
from elasticsearch import Elasticsearch

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

model_dir = "model_storage"
os.makedirs(model_dir, exist_ok=True)


def get_model_by_name(algo_name: str):
    if algo_name == "linear":
        return LinearRegression()
    elif algo_name == "logistic":
        return LogisticRegression()
    elif algo_name == "tree":
        return DecisionTreeRegressor()
    elif algo_name == "xgb":
        return XGBRegressor()
    else:
        raise ValueError(f"Unsupported algorithm: {algo_name}")


def train_model_and_save(algo_name: str):
    es = Elasticsearch("http://localhost:9200")
    index_name = "order_products-logs"

    res = es.search(index=index_name, body={"size": 10000, "query": {"match_all": {}}})

    data = []
    for hit in res['hits']['hits']:
        doc = hit['_source']
        data.append({
            "productName": doc["productName"],
            "userAge": doc["userAge"],
            "productPrice": doc["productPrice"],
            "productQuantity": doc["productQuantity"]
        })

    df = pd.DataFrame(data)
    df_grouped = df.groupby("productName").sum().reset_index()

    X = df_grouped[["userAge", "productPrice"]]
    y = df_grouped["productQuantity"]

    model = get_model_by_name(algo_name)
    model.fit(X, y)

    model_path = os.path.join(model_dir, f"model_{algo_name}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump((model, df_grouped), f)

    return {"message": f"{algo_name} model trained and saved."}
