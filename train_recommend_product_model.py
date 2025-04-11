import pandas as pd
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from xgboost import XGBClassifier
import pickle, os

model_dir = "model_storage"
os.makedirs(model_dir, exist_ok=True)

def fetch_all_es_data(index_name, es, scroll='2m', size=1000):
    all_data = []
    page = es.search(index=index_name, scroll=scroll, size=size, body={"query": {"match_all": {}}})
    sid = page['_scroll_id']
    hits = page['hits']['hits']
    all_data.extend(hits)

    while hits:
        page = es.scroll(scroll_id=sid, scroll=scroll)
        sid = page['_scroll_id']
        hits = page['hits']['hits']
        all_data.extend(hits)

    return [doc['_source'] for doc in all_data]


def train_recommend_model_and_save(algo_name: str):
    recommendation_algos = ["content", "collaborative", "svd", "xgb_classifier"]
    if algo_name in recommendation_algos:
        return train_recommendation_model(algo_name)
    else:
        raise ValueError(f"Unsupported or invalid algorithm: {algo_name}")


def train_recommendation_model(algo_name: str):
    es = Elasticsearch("http://localhost:9200")
    index_name = "order_products-logs"
    data = fetch_all_es_data(index_name, es)
    df = pd.DataFrame(data)

    # 🔹 컬럼명 정리
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["username"] = df["username"].astype(str)
    df["productName"] = df["productName"].astype(str)

    # 필드명 매칭
    df.rename(columns={
        "userAge": "age",
        "userGender": "gender",
        "userRegion": "region",
        "productName": "product"
    }, inplace=True)

    user_features = df[["username", "region", "age", "gender"]].drop_duplicates().set_index("username")

    model_path = os.path.join(model_dir, f"model_{algo_name}.pkl")

    if algo_name == "content":
        product_user_features = df.groupby("product")[["age"]].mean()
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(product_user_features)

        similarity = cosine_similarity(scaled_features)
        similarity_df = pd.DataFrame(similarity, index=product_user_features.index, columns=product_user_features.index)

        with open(model_path, "wb") as f:
            pickle.dump(similarity_df, f)

        return {"message": "Content-based filtering model trained and saved."}

    elif algo_name == "collaborative":
        user_item_matrix = df.groupby(["username", "product"]).size().unstack(fill_value=0)
        similarity = cosine_similarity(user_item_matrix)
        similarity_df = pd.DataFrame(similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

        with open(model_path, "wb") as f:
            pickle.dump(similarity_df, f)

        return {"message": "Collaborative filtering model trained and saved."}

    elif algo_name == "svd":
        user_item_matrix = df.groupby(["username", "product"]).size().unstack(fill_value=0)
        svd = TruncatedSVD(n_components=10)
        svd_matrix = svd.fit_transform(user_item_matrix)

        model_data = {
            "svd": svd,
            "user_index": user_item_matrix.index.tolist(),
            "item_columns": user_item_matrix.columns.tolist()
        }

        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)

        return {"message": "SVD recommendation model trained and saved."}

    elif algo_name == "xgb_classifier":
        # 구매된 조합 (positive sample)
        df["label"] = 1
        positive_df = df[["username", "product", "age", "gender", "region", "label"]]

        # 사용자 및 상품 목록
        users = df["username"].unique()
        products = df["product"].unique()

        # 음성 샘플 생성 (랜덤 사용자-상품 조합 중 실제 구매한 것 제외)
        import random

        neg_samples = []
        existing_pairs = set(zip(df["username"], df["product"]))

        while len(neg_samples) < len(positive_df):
            user = random.choice(users)
            product = random.choice(products)
            if (user, product) not in existing_pairs:
                user_info = user_features.loc[user]
                neg_samples.append({
                    "username": user,
                    "product": product,
                    "age": user_info["age"],
                    "gender": user_info["gender"],
                    "region": user_info["region"],
                    "label": 0
                })

        negative_df = pd.DataFrame(neg_samples)
        train_df = pd.concat([positive_df, negative_df], ignore_index=True)

        encoded_gender = train_df["gender"].map({"남": 0, "여": 1})
        X = pd.DataFrame({
            "age": train_df["age"],
            "gender": encoded_gender,
            "region": train_df["region"].astype("category").cat.codes,
            "product": train_df["product"].astype("category").cat.codes
        })
        y = train_df["label"]

        model = XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss')
        model.fit(X, y)

        model_data = {
            "model": model,
            "product_encoder": dict(zip(df["product"], df["product"].astype("category").cat.codes)),
            "region_encoder": dict(zip(df["region"], df["region"].astype("category").cat.codes)),
        }

        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)

        return {"message": "XGBoost classifier recommendation model trained and saved."}

    else:
        raise ValueError(f"Unsupported recommendation model: {algo_name}")
