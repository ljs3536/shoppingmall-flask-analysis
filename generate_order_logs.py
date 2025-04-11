from datetime import datetime, timedelta
import random
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")

usernames = ["user01", "user02", "user03", "user04", "user05","user06","user07","user08","user09","user10"
             ,"user11", "user12", "user13", "user14", "user15","user16","user17","user18","user19","user20"
             ,"user21", "user22", "user23", "user24", "user25","user26","user27","user28","user29","user30"
             ,"user31", "user32", "user33", "user34", "user35","user36","user37","user38","user39","user40"
             ,"user41", "user42", "user43", "user44", "user45","user46","user47","user48","user49","user50"
             ,"user51", "user52", "user53", "user54", "user55","user56","user57","user58","user59","user60"
             ,"user61", "user62", "user63", "user64", "user65","user66","user67","user68","user69","user70"
             ,"user71", "user72", "user73", "user74", "user75","user76","user77","user78","user79","user80"
             ,"user81", "user82", "user83", "user84", "user85","user86","user87","user88","user89","user90"
             ,"user91", "user92", "user93", "user94", "user95","user96","user97","user98","user99","user100"]
regions = ["서울", "대전", "부산", "광주", "인천","대구","울산","강릉","전주","천안"
           ,"서울", "서울", "부산", "광주", "인천","대구","울산","서울","전주","천안"
           ,"서울", "대전", "천안", "광주", "인천","서울","울산","세종","전주","천안"
           ,"서울", "서울", "부산", "서울", "인천","대구","울산","강릉","서울","서울"
           ,"서울", "대전", "세종", "광주", "서울","서울","서울","강릉","전주","천안"
           ,"서울", "울산", "부산", "광주", "인천","대구","울산","부산","전주","천안"
           ,"서울", "대전", "부산", "서울", "서울","세종","울산","강릉","세종","서울"
           ,"서울", "서울", "서울", "광주", "인천","대구","서울","서울","전주","천안"
           ,"서울", "대전", "부산", "광주", "서울","대구","세종","강릉","세종","서울"
           ,"서울", "대전", "부산", "광주", "인천","대구","울산","강릉","전주","천안"]
genders = ["남", "여"]
ages = list(range(10, 80))

products = [  # 동일한 제품 리스트 유지
    {"name": "노트북1", "price": 11200000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "스마트폰1", "price": 1900000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "헤드폰1", "price": 2150000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "노트북2", "price": 1200000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "스마트폰2", "price": 900000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "헤드폰2", "price": 50000, "category": "전자제품", "sellerId": "testseller1"},
    {"name": "볼펜1", "price": 2000, "category": "생활용품", "sellerId": "testseller1"},
    {"name": "볼펜2", "price": 4000, "category": "생활용품", "sellerId": "testseller1"},
    {"name": "볼펜3", "price": 12000, "category": "생활용품", "sellerId": "testseller1"},
    {"name": "가위1", "price": 3000, "category": "생활용품", "sellerId": "testseller1"},
    {"name": "물티슈1", "price": 120000, "category": "생활용품", "sellerId": "testseller1"},
    {"name": "물티슈2", "price": 20000, "category": "생활용품", "sellerId": "testseller11"},
    {"name": "물티슈3", "price": 320000, "category": "생활용품", "sellerId": "testseller11"},
    {"name": "휴지1", "price": 50000, "category": "생활용품", "sellerId": "testseller12"},
    {"name": "운동화1", "price": 120000, "category": "패션", "sellerId": "testseller13"},
    {"name": "청바지1", "price": 50000, "category": "패션", "sellerId": "testseller13"},
    {"name": "운동화2", "price": 20000, "category": "패션", "sellerId": "testseller13"},
    {"name": "청바지2", "price": 150000, "category": "패션", "sellerId": "testseller13"},
    {"name": "코트1", "price": 2000000, "category": "패션", "sellerId": "testseller13"},
    {"name": "코트2", "price": 250000, "category": "패션", "sellerId": "testseller13"},
    {"name": "코트3", "price": 8000000, "category": "패션", "sellerId": "testseller13"},
    {"name": "가디건1", "price": 100000, "category": "패션", "sellerId": "testseller13"},
    {"name": "가디건2", "price": 150000, "category": "패션", "sellerId": "testseller13"},
    {"name": "가디건3", "price": 80000, "category": "패션", "sellerId": "testseller13"},
    {"name": "핸드크림1", "price": 12000, "category": "화장품", "sellerId": "testseller12"},
    {"name": "선크림1", "price": 30000, "category": "화장품", "sellerId": "testseller12"},
    {"name": "핸드크림2", "price": 50000, "category": "화장품", "sellerId": "testseller12"},
    {"name": "선크림2", "price": 22000, "category": "화장품", "sellerId": "testseller12"},
    {"name": "핸드크림3", "price": 56000, "category": "화장품", "sellerId": "testseller12"},
    {"name": "선크림3", "price": 10000, "category": "화장품", "sellerId": "testseller12"},
]

positive_reviews = [
    "정말 만족스러워요!", "좋은 제품이에요", "다시 구매하고 싶어요", "추천합니다", "가성비 최고!", "또 구매했어요"
]

negative_reviews = [
    "별로에요", "품질이 기대 이하에요", "다시는 안살래요", "돈이 아까워요", "실망했어요", "이런상품 팔지마라"
]

def generate_order_log(days=365*5):
    order_actions = []
    review_actions = []
    start_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        log_date = start_date + timedelta(days=day)
        num_logs_per_day = random.randint(30, 200)
        for _ in range(num_logs_per_day):
            index = random.randint(0, 99)
            user = usernames[index]
            age = random.choice(ages)
            region = regions[index]
            gender = random.choice(genders)
            product = random.choice(products)
            quantity = random.randint(1, 5)
            order_type = random.choice(["CART", "DIRECT"])

            order_doc = {
                "timestamp": log_date.strftime("%Y-%m-%d"),
                "orderType": order_type,
                "username": user,
                "userAge": age,
                "userRegion": region,
                "userGender": gender,
                "productName": product["name"],
                "productPrice": product["price"],
                "productCategory": product["category"],
                "sellerId": product["sellerId"],
                "productQuantity": quantity
            }

            order_actions.append({
                "_index": "order_products-logs",
                "_source": order_doc
            })

            # 리뷰 생성 확률: 70%
            if random.random() < 0.7:
                rating = random.randint(1, 5)
                if rating >= 4:
                    description = random.choice(positive_reviews)
                else:
                    description = random.choice(negative_reviews)

                review_doc = {
                    "timestamp": log_date.strftime("%Y-%m-%d"),
                    "userId": user,
                    "userAge": age,
                    "userRegion": region,
                    "userGender": gender,
                    "productName": product["name"],
                    "productPrice": product["price"],
                    "productCategory": product["category"],
                    "productQuantity": quantity,
                    "sellerId": product["sellerId"],
                    "rating": rating,
                    "description": description
                }

                review_actions.append({
                    "_index": "review_products-logs",
                    "_source": review_doc
                })

    # bulk insert
    helpers.bulk(es, order_actions)
    helpers.bulk(es, review_actions)
    print(f"{len(order_actions)}개의 주문 로그 생성 완료")
    print(f"{len(review_actions)}개의 리뷰 로그 생성 완료")


# 실행 시
#generate_order_log()
