import json
import pandas as pd
from django.http import JsonResponse
from .views import get_hive_connection


def customer_analysis(request):
    # Đây là ví dụ
    data_prime = {
        "total_customers": [300, 200],
        "gender_distribution": ["M", "F"],
        "country_distribution": ["None", "Now"]
    }
    df = pd.DataFrame(data_prime)
    
    # Gửi Json Response
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)
    # Kết nối với Hive
    # Connect to Hive
    conn = get_hive_connection()
    query = """
    SELECT customer_id, gender, home_country, SUM(total_amount) AS total_spent
    FROM transaction
    JOIN customer ON transaction.customer_id = customer.customer_id
    GROUP BY customer.customer_id, customer.gender, customer.home_country
    """
    df = pd.read_sql(query, conn)
    print(df)
    # Total number of customers
    total_customers = df["customer_id"].nunique()

    # Customer demographics (e.g., gender, home country)
    gender_distribution = df["gender"].value_counts().to_dict()
    country_distribution = df["home_country"].value_counts().to_dict()

    # Returning analysis data as JSON
    data = {
        "total_customers": total_customers,
        "gender_distribution": gender_distribution,
        "country_distribution": country_distribution,
    }
    return JsonResponse(data)


def transaction_analysis(request):
    conn = get_hive_connection()
    query = """
    SELECT created_at, SUM(total_amount) AS total_revenue
    FROM transaction
    GROUP BY created_at
    ORDER BY created_at
    """
    df = pd.read_sql(query, conn)

    # Calculate total revenue and trends
    total_revenue = df["total_revenue"].sum()
    revenue_trends = df.set_index("created_at")["total_revenue"].to_dict()

    data = {"total_revenue": total_revenue, "revenue_trends": revenue_trends}
    return JsonResponse(data)


def product_analysis(request):
    conn = get_hive_connection()

    # Updated Hive query to handle JSON

    # create_view_query = """
    # CREATE OR REPLACE VIEW temp_transaction AS
    # SELECT regexp_replace(product_metadata, '^"|"$', '') as product_metadata
    # FROM transaction
    # """

    select_query = """
SELECT 
       get_json_object(temp_transaction.col, '$.product_id') AS product_id,
       get_json_object(temp_transaction.col, '$.item_price') AS item_price,
       get_json_object(temp_transaction.col, '$.quantity') AS quantity
FROM ( SELECT explode (
  split(regexp_replace(substr(product_metadata, 2, length(product_metadata)-2),
            '"}","', '"}",,,,"'), ',,,,')
      ) FROM transaction) temp_transaction
"""
    # analyzing the data
    df = pd.read_sql(select_query, conn)
    df["item_price"] = pd.to_numeric(df["item_price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    # Drop rows with NaN values in item_price or quantity
    df.dropna(subset=["item_price", "quantity"], inplace=True)

    # Total revenue generated by each product
    df["total_revenue"] = df["item_price"] * df["quantity"]
    total_revenue_by_product = (
        df.groupby("product_id")["total_revenue"].sum().head(5).to_dict()
    )

    # Most sold products
    most_sold_products = df.groupby("product_id")["quantity"].sum().head(5).to_dict()

    data = {
        "most_sold_products": most_sold_products,
        "total_revenue_by_product": total_revenue_by_product,
    }
    return JsonResponse(data)


def behavioral_analysis(request):
    conn = get_hive_connection()
    #     query = """
    # SELECT
    # get_json_object(event_metadata, '$.product_id') AS product_id,
    # get_json_object(event_metadata, '$.item_price') AS item_price,
    # get_json_object(event_metadata, '$.quantity') AS quantity,
    # get_json_object(event_metadata, '$.search_keywords') AS search_keywords,
    # get_json_object(event_metadata, '$.promo_code') AS promo_code,
    # get_json_object(event_metadata, '$.promo_amount') AS promo_amount,
    # get_json_object(event_metadata, '$.payment_status') AS payment_status
    # FROM click_stream
    #     """
    query = """
    SELECT product_id, COUNT(*) AS total_interactions
    FROM (
        SELECT get_json_object(event_metadata, '$.product_id') AS product_id
        FROM click_stream
        WHERE event_name = 'ADD_TO_CART'
    ) AS subquery
    GROUP BY product_id
    ORDER BY total_interactions DESC
    """
    df = pd.read_sql(query, conn)
    df["percentage_interactions"] = (
        df["total_interactions"] / df["total_interactions"].sum() * 100
    )
    # # how to analyze the semi-structured data
    # def safe_json_loads(x):
    #     try:
    #         return json.loads(x)
    #     except (json.JSONDecodeError, TypeError):
    #         return None

    # df["col"] = df["col"].apply(safe_json_loads)
    # print(df["col"])
    # df = df.dropna(subset=["col"])
    # normalized_df = pd.json_normalize(df["col"], errors="ignore")
    # print(df)
    # most_viewed_products = (
    #     normalized_df["search_keywords"].value_counts().head(5).to_dict()
    # )

    data = {"most_viewed_products": df.to_dict(orient="records")}
    return JsonResponse(data)


def multiple_analysis(request):
    conn = get_hive_connection()
    query = """
    SELECT promo_code, COUNT(*) AS usage_count, SUM(promo_amount) AS total_discount
    FROM (
        SELECT get_json_object(event_metadata, '$.promo_code') AS promo_code,
            CAST(get_json_object(event_metadata, '$.promo_amount') AS FLOAT) AS promo_amount
        FROM click_stream
        WHERE event_name = 'ADD_PROMO'
    ) AS subquery
    GROUP BY promo_code
    ORDER BY usage_count DESC
    """
    df = pd.read_sql(query, conn)
    query = """
        SELECT COUNT(*) AS total_payment
        FROM click_stream
        WHERE event_name = 'BOOKING'
    """
    total_payment = pd.read_sql(query, conn)["total_payment"].values[0]
    df["usage_count_percentage"] = df["usage_count"] / total_payment * 100
    df.to_csv("multiple_analysis.csv", index=False)
    data = {
        "promo_usage_percentage": df["usage_count_percentage"].sum(),
        "multiple_analysis": df.to_dict(orient="records"),
    }
    return JsonResponse(data)


def keyword_analysis(request):
    # Đây là ví dụ
    data_prime = {
        "month": [1, 1, 2],
        "search_keywords": ["None", "AZ2022", "BUYMORE"],
        "search_count": [100, 200, 100]
    }
    df = pd.DataFrame(data_prime)
    
    # Gửi Json Response
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)
    # Kết nối với Hive
    conn = get_hive_connection()
    query = """
    SELECT month, search_keywords, search_count
    FROM (
        SELECT 
            date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM') AS month, 
            get_json_object(event_metadata, '$.search_keywords') AS search_keywords,
            COUNT(*) AS search_count,
            ROW_NUMBER() OVER (PARTITION BY date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM') ORDER BY COUNT(*) DESC) AS rank
        FROM click_stream
        WHERE event_name = 'SEARCH'
        GROUP BY date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM'), get_json_object(event_metadata, '$.search_keywords')
    ) AS subquery
    WHERE rank <= 5 
    ORDER BY month ASC, search_count DESC
    """
    df = pd.read_sql(query, conn)

    df.to_csv("keyword_analysis.csv", index=False)
    data = {"search_keywords": df.to_dict(orient="records")}
    return JsonResponse(data)


def get_product_sucessorder_percentage_analysis(request):
    conn = get_hive_connection()
    query = """
    SELECT product_id, SUM(quantity) AS total_interactions
    FROM (
        SELECT get_json_object(event_metadata, '$.product_id') AS product_id, get_json_object(event_metadata, '$.quantity') AS quantity 
        FROM click_stream
        WHERE event_name = 'ADD_TO_CART'
    ) AS subquery
    GROUP BY product_id
    ORDER BY total_interactions DESC
    """
    df = pd.read_sql(query, conn)
    success_order_query = """
    SELECT 
       get_json_object(temp_transaction.col, '$.product_id') AS product_id,
       get_json_object(temp_transaction.col, '$.quantity') AS quantity
FROM ( SELECT explode (
  split(regexp_replace(substr(product_metadata, 2, length(product_metadata)-2),
            '"}","', '"}",,,,"'), ',,,,')
      ) FROM transaction
      WHERE payment_status = 'Success'
      ) temp_transaction
    """
    df_success_order = pd.read_sql(success_order_query, conn)

    df_success_order["quantity"] = df_success_order["quantity"].astype(int)
    df_success_order = (
        df_success_order.groupby("product_id")["quantity"].sum().reset_index()
    )
    get_product_query = """
    SELECT id, productDisplayName FROM
    product
    """
    product_df = pd.read_sql(get_product_query, conn)
    product_df.rename(columns={"id": "product_id"}, inplace=True)
    df_merged = pd.merge(
        df,
        df_success_order,
        on="product_id",
        suffixes=("_total", "_success"),
    )
    df_merged = pd.merge(
        df_merged,
        product_df,
        on="product_id",
    )
    df_merged["success_order_percentage"] = (
        df_merged["quantity"] / df_merged["total_interactions"]
    ) * 100
    df_merged[["productdisplayname", "success_order_percentage"]].to_csv(
        "successorder.csv", index=False
    )
    data = {
        "top_10_product": df_merged[
            ["productdisplayname", "success_order_percentage"]
        ].to_dict(orient="records"),
        "bot_10_product": df_merged[
            ["productdisplayname", "success_order_percentage"]
        ].to_dict(orient="records"),
    }

    return JsonResponse(data)


def keyword_analysis_bymonth(request, month=None):
    month_param = request.GET.get("month", month)
    conn = get_hive_connection()
    query = (
        """
    SELECT month, search_keywords, search_count
    FROM (
        SELECT 
            date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM') AS month, 
            get_json_object(event_metadata, '$.search_keywords') AS search_keywords,
            COUNT(*) AS search_count,
            ROW_NUMBER() OVER (PARTITION BY date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM') ORDER BY COUNT(*) DESC) AS rank
        FROM click_stream
        WHERE event_name = 'SEARCH'
        GROUP BY date_format(from_unixtime(unix_timestamp(event_time, "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'")), 'MM'), get_json_object(event_metadata, '$.search_keywords')
    ) AS subquery
    WHERE rank <= 5 AND month = """
        + str(month_param)
        + """
    ORDER BY month ASC, search_count DESC
    """
    )
    df = pd.read_sql(query, conn)
    data = {"search_keywords": df.to_dict(orient="records")}
    return JsonResponse(data)


def get_code_analysis(request):
    # Đây là ví dụ
    data_prime = {
        "promo_code": ["None", "AZ2022", "BUYMORE"],
        "TOTAL_AMOUNT": [3.788477e+10, 6.675745e+09, 4.962927e+09],
        "PROMO_AMOUNT": [0, 60119641, 44486761],
        "COUNT": [0, 12005, 8942],
        "START_DAY": ["2016-08-07T09:22:39.501036Z", "2016-08-08T06:25:24.341833Z", "2016-08-08T03:46:50.958678Z"],
        "END_DAY": ["2022-07-31T23:16:43.885323Z", "2022-07-29T22:16:37.169906Z", "2022-07-29T12:48:21.123459Z"]
    }
    df = pd.DataFrame(data_prime)
    
    # Gửi Json Response
    data = df.to_dict(orient="records")
    return JsonResponse(data, safe=False)
    # Kết nối đến Hive
    conn = get_hive_connection()

    # Truy vấn lấy dữ liệu khách hàng từ bảng 'transaction' và 'customer'
    query = """
        SELECT promo_code, SUM(total_amount) AS TOTAL_AMOUNT, 
        SUM(promo_amount) AS PROMO_AMOUNT, COUNT(promo_code) AS COUNT, 
        MIN(created_at) as START_DAY, MAX(created_at) as END_DAY 
        FROM transactions
        WHERE payment_status = 'Success' 
        GROUP BY promo_code
    """
    df = pd.read_sql(query, conn)

    if df.empty:
        return JsonResponse({"error": "No data found"}, status=400)

    # Gửi Json Response
    data = df.to_dict(orient="records")
    return JsonResponse(data)

def customer_segmentation(request):
    # Kết nối đến Hive
    conn = get_hive_connection()

    # Truy vấn lấy dữ liệu khách hàng từ bảng 'transaction' và 'customer'
    query = """
    SELECT customer_id, gender, home_country, SUM(total_amount) AS total_spent
    FROM transaction
    JOIN customer ON transaction.customer_id = customer.customer_id
    GROUP BY customer.customer_id, customer.gender, customer.home_country
    """
    df = pd.read_sql(query, conn)

    if df.empty:
        return JsonResponse({"error": "No data found"}, status=400)

    quantiles = df["total_spent"].quantile([0.25, 0.50, 0.75, 1.0])

    # Phân nhóm khách hàng theo các percentiles
    bins = [0, quantiles[0.25], quantiles[0.50], quantiles[0.75], quantiles[1.0]]
    labels = ["Low", "Medium", "High", "Very High"]
    df["spending_group"] = pd.cut(
        df["total_spent"], bins=bins, labels=labels, include_lowest=True
    )

    # Phân tích thống kê
    segmentation = (
        df.groupby(["spending_group", "gender", "home_country"])
        .size()
        .reset_index(name="count")
    )

    # Tạo dữ liệu phân tích phân khúc khách hàng
    data = {
        "total_customers": df["customer_id"].nunique(),
        "segmentation": segmentation.to_dict(orient="records"),
    }

    return JsonResponse(data)
