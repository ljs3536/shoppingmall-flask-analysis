import pickle
import os
import pandas as pd

model_dir = "model_storage"

def predict_quantity(product_name: str, algo_name: str):
    model_path = os.path.join(model_dir, f"model_{algo_name}.pkl")

    if not os.path.exists(model_path):
        return {"error": "Model not found. Please train the model first."}

    with open(model_path, "rb") as f:
        model, df = pickle.load(f)

    product = df[df["productName"] == product_name]
    if product.empty:
        return {"error": "Product not found in training data."}

    X = product[["userAge", "productPrice"]]
    prediction = model.predict(X)

    return {
        "productName": product_name,
        "predictedQuantity": round(prediction[0], 2),
        "algorithm": algo_name
    }
