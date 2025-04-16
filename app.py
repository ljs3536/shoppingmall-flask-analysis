from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from generate_cart_logs import generate_cart_log
from generate_order_logs import generate_order_log
from search_handler import get_yearly_sales, get_age_group_favorites, get_region_favorites, get_monthly_category_trend, get_gender_favorites
from train_order_product_model import train_predict_model_and_save
from predict_order_product_model import predict_quantity_pipeline
from train_recommend_product_model import train_recommend_model_and_save
from predict_recommend_product_model import predict_recommendation_pipeline
from search_Recommend import get_trendingProducts, get_addedCartProducts, get_moreSellingProducts, get_popularProducts_category, get_highRatedProducts
app = Flask(__name__)

# Elasticsearch 연결 (Docker 컨테이너에서 실행 중일 경우)
es = Elasticsearch("http://elasticsearch-container:9200")

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

@app.route("/search/products/age", methods=["GET"])
def age_group_favorites():
    return jsonify(get_age_group_favorites())

@app.route("/search/products/region", methods=["GET"])
def region_favorites():
    return jsonify(get_region_favorites())

@app.route("/search/products/trend", methods=["GET"])
def monthly_trend():
    return jsonify(get_monthly_category_trend())

@app.route("/search/products/gender", methods=["GET"])
def gender_favorites():
    return jsonify(get_gender_favorites())

@app.route("/search/products/moreSelling", methods=["GET"])
def more_selling():
    seller_id = request.args.get("sellerId")
    return jsonify(get_moreSellingProducts(seller_id))

@app.route("/search/products/popularByCategory", methods=["GET"])
def popular_by_category():
    seller_id = request.args.get("sellerId")
    return jsonify(get_popularProducts_category(seller_id))

@app.route("/search/products/addedCart", methods=["GET"])
def added_cart():
    seller_id = request.args.get("sellerId")
    return jsonify(get_addedCartProducts(seller_id))

@app.route("/search/products/highRated", methods=["GET"])
def high_rated():
    seller_id = request.args.get("sellerId")
    return jsonify(get_highRatedProducts(seller_id))

@app.route("/search/products/trending", methods=["GET"])
def trending():
    seller_id = request.args.get("sellerId")
    return jsonify(get_trendingProducts(seller_id))

@app.route("/predict/train", methods=["POST"])
def train_predict_model():
    algo_name = request.json.get("algo_name")
    print(algo_name)
    result = train_predict_model_and_save(algo_name)
    return jsonify(result)

@app.route("/predict/product", methods=["GET"])
def predict_product_quantity():
    product_name = request.args.get("productName")
    algo_name = request.args.get("algo", default="linear")
    print(product_name, " : " , algo_name)
    if not product_name:
        return jsonify({"error": "productName parameter is required"}), 400

    result = predict_quantity_pipeline(product_name, algo_name)
    return jsonify(result)

@app.route("/recommend/train", methods=["POST"])
def train_recommend_model():
    algo_name = request.json.get("algo_name")
    print(algo_name)
    result = train_recommend_model_and_save(algo_name)
    return jsonify(result)

@app.route("/recommend/product", methods=["POST"])
def predict_product_recommend():
    user_info = request.json.get("user_info")
    algo_name = request.args.get("algo", default="linear")

    if not user_info:
        return jsonify({"error": "user_info parameter is required"}), 400

    result = predict_recommendation_pipeline(user_info, algo_name)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
