from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from generate_cart_logs import generate_cart_log
from generate_order_logs import generate_order_log
from search_handler import get_yearly_sales
from train_order_product_model import train_model_and_save
from predict_order_product_model import predict_quantity

app = Flask(__name__)

# Elasticsearch 연결 (Docker 컨테이너에서 실행 중일 경우)
es = Elasticsearch("http://localhost:9200")

@app.route("/search", methods=["GET"])
def search_logs():
    keyword = request.args.get("keyword", "")
    index_name = "access-log"  # 로그가 저장된 인덱스 이름

    query = {
        "query": {
            "match": {
                "userId": keyword
            }
        }
    }

    res = es.search(index=index_name, body=query)
    return jsonify(res["hits"]["hits"])

# /generate/cart 엔드포인트
@app.route('/generate/cart', methods=['GET'])
def generate_cart_logs():
    generate_cart_log()
    return jsonify({"message": "Cart logs generated!"})

# /generate/order 엔드포인트
@app.route('/generate/order', methods=['GET'])
def generate_order_logs():
    generate_order_log()
    return jsonify({"message": "Order logs generated!"})

@app.route("/search/products/years", methods=["GET"])
def get_sales_by_year():
    year = request.args.get("year")
    if not year:
        return jsonify({"error": "year parameter required"}), 400

    data = get_yearly_sales(year)
    return jsonify(data)

@app.route("/predict/train", methods=["POST"])
def train_model():
    result = train_model_and_save()
    return jsonify(result)

@app.route("/predict/product", methods=["GET"])
def predict_product_quantity():
    product_name = request.args.get("productName")
    if not product_name:
        return jsonify({"error": "productName parameter is required"}), 400

    result = predict_quantity(product_name)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
