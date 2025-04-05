from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Elasticsearch 연결 (Docker 컨테이너에서 실행 중일 경우)
es = Elasticsearch("http://localhost:9200")

@app.route("/search", methods=["GET"])
def search_logs():
    keyword = request.args.get("keyword", "")
    index_name = "accesslog"  # 로그가 저장된 인덱스 이름

    query = {
        "query": {
            "match": {
                "message": keyword  # 'message' 필드에서 검색
            }
        }
    }

    res = es.search(index=index_name, body=query)
    return jsonify(res["hits"]["hits"])

if __name__ == "__main__":
    app.run(debug=True)
