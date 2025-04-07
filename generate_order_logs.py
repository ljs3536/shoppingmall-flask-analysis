from datetime import datetime, timedelta
import random
from elasticsearch import Elasticsearch, helpers

# Elasticsearch 연결
es = Elasticsearch("http://localhost:9200")

# 샘플 데이터 정의
usernames = ["user01", "user02", "user03", "user04", "user05","user06","user07","user08","user09","user10"]
regions = ["서울", "대전", "부산", "광주", "인천","대구","울산","강릉","전주","천안"]
genders = ["남", "여"]
ages = list(range(10, 60))  # 10세~60세
products = [
    {"name": "노트북1", "price": 11200000, "category": "전자제품"},
    {"name": "스마트폰1", "price": 1900000, "category": "전자제품"},
    {"name": "헤드폰1", "price": 2150000, "category": "전자제품"},
    {"name": "노트북2", "price": 1200000, "category": "전자제품"},
    {"name": "스마트폰2", "price": 900000, "category": "전자제품"},
    {"name": "헤드폰2", "price": 50000, "category": "전자제품"},
    {"name": "노트북3", "price": 200000, "category": "전자제품"},
    {"name": "스마트폰3", "price": 90000, "category": "전자제품"},
    {"name": "헤드폰3", "price": 250000, "category": "전자제품"},
    {"name": "볼펜1", "price": 2000, "category": "생활용품"},
    {"name": "볼펜2", "price": 4000, "category": "생활용품"},
    {"name": "볼펜3", "price": 12000, "category": "생활용품"},
    {"name": "가위1", "price": 3000, "category": "생활용품"},
    {"name": "물티슈1", "price": 120000, "category": "생활용품"},
    {"name": "물티슈2", "price": 20000, "category": "생활용품"},
    {"name": "물티슈3", "price": 320000, "category": "생활용품"},
    {"name": "휴지1", "price": 50000, "category": "생활용품"},
    {"name": "운동화1", "price": 120000, "category": "패션"},
    {"name": "청바지1", "price": 50000, "category": "패션"},
    {"name": "운동화2", "price": 20000, "category": "패션"},
    {"name": "청바지2", "price": 150000, "category": "패션"},
    {"name": "핸드크림1", "price": 12000, "category": "화장품"},
    {"name": "선크림1", "price": 30000, "category": "화장품"},
    {"name": "핸드크림2", "price": 50000, "category": "화장품"},
    {"name": "선크림2", "price": 22000, "category": "화장품"},
    {"name": "핸드크림3", "price": 56000, "category": "화장품"},
    {"name": "선크림3", "price": 10000, "category": "화장품"},
]

# 데이터 생성 함수
def generate_order_log(days=730, num_logs_per_day=100):
    actions = []
    start_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        log_date = start_date + timedelta(days=day)
        for _ in range(num_logs_per_day):
            index = random.randint(0, 9)
            user = usernames[index]
            age = random.choice(ages)
            region = regions[index]
            gender = random.choice(genders)
            product = random.choice(products)
            quantity = random.randint(1, 5)

            order_log = {
                "_index": "order_products-logs",
                "_source": {
                    "timestamp": log_date.strftime("%Y-%m-%d"),
                    "username": user,
                    "userAge": age,
                    "userRegion": region,
                    "userGender": gender,
                    "productName": product["name"],
                    "productPrice": product["price"],
                    "productCategory": product["category"],
                    "productQuantity": quantity
                }
            }
            actions.append(order_log)

            # 50% 확률로 주문 로그 생성
            if random.random() < 0.5:
                order_log = order_log.copy()
                order_log["_index"] = "order_products-logs"
                actions.append(order_log)

    # 데이터 Elasticsearch에 저장
    helpers.bulk(es, actions)
    print(f"{len(actions)}개의 로그가 생성되었습니다!")

# 실행
generate_order_log()

