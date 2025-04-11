import pandas as pd
import pickle
import os
from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA

from datetime import datetime
from dateutil.relativedelta import relativedelta

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

model_dir = "test_model_storage"
os.makedirs(model_dir, exist_ok=True)

# 시각화 함수 정의
def plot_ts(data, color, alpha, label):
    plt.figure(figsize=(11, 5))
    plt.plot(data, color=color, alpha=alpha, label=label)
    plt.title("productQuantity of Monthly")
    plt.ylabel('productQuantity')
    plt.legend()
    plt.show()

def fetch_all_es_data(index_name, es, scroll='2m', size=1000):
    all_data = []
    page = es.search(
        index=index_name,
        scroll=scroll,
        size=size,
        body={"query": {"match_all": {}}}
    )
    sid = page['_scroll_id']
    hits = page['hits']['hits']
    all_data.extend(hits)

    while len(hits) > 0:
        page = es.scroll(scroll_id=sid, scroll=scroll)
        sid = page['_scroll_id']
        hits = page['hits']['hits']
        all_data.extend(hits)

    return [doc['_source'] for doc in all_data]
def train_timeseries_model():
    es = Elasticsearch("http://localhost:9200")
    index_name = "order_products-logs"
    data = fetch_all_es_data(index_name, es)
    df = pd.DataFrame(data)
    print(df)
    # 날짜 변환 및 필터링
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["year_month"] = df["timestamp"].dt.to_period("M")

    print("날짜 변환 및 필터링 ")
    print(df)

    # 월별 판매량 집계
    monthly_sales = df.groupby(["productName", "year_month"])["productQuantity"].sum().reset_index()
    monthly_sales["year_month"] = monthly_sales["year_month"].astype(str)
    monthly_sales["year_month"] = pd.to_datetime(monthly_sales["year_month"])
    monthly_sales = monthly_sales.sort_values(["productName", "year_month"])

    # print("월별 판매량", monthly_sales)
    # print(df_product)
    # df_product2 = df_product.loc[:, ['year_month', 'productQuantity']]
    # df_product2 = df_product2.set_index("year_month")
    # print(df_product2)
    # all_months = pd.date_range(
    #     start=monthly_sales["year_month"].min(),
    #     end=monthly_sales["year_month"].max(),
    #     freq="MS"
    # )
    # df_product = df_product.set_index("year_month").reindex(all_months)
    models = {}

    for product in monthly_sales["productName"].unique():
        df_product = monthly_sales[monthly_sales["productName"] == product].copy()
        # 🔹 누락된 월 채우기 (보간)
        all_months = pd.date_range(
            start=monthly_sales["year_month"].min(),
            end=monthly_sales["year_month"].max(),
            freq="MS"
        )
        # 날짜를 index로 바꿔서 시계열 처럼 다루기 쉽도록 함
        df_product = df_product.set_index("year_month").reindex(all_months)
        df_product.index.name = "year_month"
        df_product["productName"] = product
        # 누락 되었던 월의 productQuantity 부분의 데이터 선형 보간
        df_product["productQuantity"] = df_product["productQuantity"].astype(float).interpolate(method="linear")
        # index로 변했던 부분을 다시 일반 컬럼으로 되돌림
        df_product = df_product.reset_index()

        try:
            model = ARIMA(df_product["productQuantity"], order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=4)
            last_date = df_product["year_month"].max()

            models[product] = {
                "model": model_fit,
                "predictions": forecast.tolist(),
                "last_date": last_date
            }
        except Exception as e:
            print(f"ARIMA failed for {product}: {e}")
            continue
    df_product = monthly_sales[monthly_sales["productName"] == "노트북1"].copy()

    print(df_product)

    #plot_ts(df_product2, "blue", 0.25, 'Original')

