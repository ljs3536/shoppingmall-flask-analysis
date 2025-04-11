import pickle
import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model_dir = "model_storage"

def predict_recommendation_pipeline(user_info: dict, algo: str):
    model_path = os.path.join(model_dir, f"model_{algo}.pkl")

    if not os.path.exists(model_path):
        return {"error": f"Model file not found for algorithm: {algo}"}

    with open(model_path, "rb") as f:
        model_data = pickle.load(f)

    if algo == "content":
        # 콘텐츠 기반: 사용자와 유사한 product feature 찾기
        similarity_df = model_data
        # 간단히 age로 product 평균 age와 비교 (확장 가능)
        user_age = user_info.get("age", 30)
        # 가장 유사한 상품 상위 N개
        similarity_scores = abs(similarity_df.mean(axis=1) - user_age)
        top_products = similarity_scores.sort_values().head(5).index.tolist()

        return {
            "algorithm": algo,
            "recommended_products": top_products
        }

    elif algo == "collaborative":
        similarity_df = model_data
        # 단순히 가장 유사도가 높은 사용자 5명 → 그들이 산 제품을 추천
        user_id = str(user_info.get("username", ""))
        if user_id not in similarity_df.index:
            return {"error": "User not found in collaborative matrix"}

        similar_users = similarity_df.loc[user_id].sort_values(ascending=False).head(5).index.tolist()
        # 기존 구매 로그에서 비슷한 사용자들이 많이 구매한 상품을 추천
        # ※ 실제 운영 시에는 구매 로그 전체에서 유사 사용자 상품 수집 필요
        return {
            "algorithm": algo,
            "recommended_users": similar_users,
            "note": "추가적으로 이들의 구매 로그를 활용해 제품을 추출해야 합니다."
        }

    elif algo == "svd":
        svd_model = model_data["svd"]
        user_index = model_data["user_index"]
        item_columns = model_data["item_columns"]

        # 새 사용자라면 zero 벡터 또는 평균으로 대체
        user_vector = np.zeros((1, len(item_columns)))
        svd_user_proj = svd_model.transform(user_vector)
        scores = svd_model.inverse_transform(svd_user_proj).flatten()
        top_indices = scores.argsort()[-5:][::-1]
        top_products = [item_columns[i] for i in top_indices]

        return {
            "algorithm": algo,
            "recommended_products": top_products
        }

    elif algo == "xgb_classifier":
        model = model_data["model"]
        product_encoder = model_data["product_encoder"]
        region_encoder = model_data["region_encoder"]

        age = user_info.get("age", 30)
        gender = 0 if user_info.get("gender") == "M" else 1
        region = region_encoder.get(user_info.get("region", ""), 0)

        X_input = []
        product_map = {}
        for product, code in product_encoder.items():
            X_input.append([age, gender, region, code])
            product_map[code] = product

        preds = model.predict_proba(np.array(X_input))[:, 1]
        top_indices = preds.argsort()[-5:][::-1]
        top_products = [product_map[X_input[i][3]] for i in top_indices]

        return {
            "algorithm": algo,
            "recommended_products": top_products
        }

    else:
        return {"error": f"Unsupported algorithm: {algo}"}
