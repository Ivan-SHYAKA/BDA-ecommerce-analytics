from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SparkSQLAnalytics") \
    .config("spark.driver.memory", "3g") \
    .getOrCreate()

transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")
users = spark.read.option("multiline", "true").json("dataset/data/users.json")

# Register as temp views
transactions.createOrReplaceTempView("transactions")
users.createOrReplaceTempView("users")

# Simple test query
result = spark.sql("""
    SELECT payment_method, COUNT(*) as count, AVG(total) as avg_total
    FROM transactions
    GROUP BY payment_method
    ORDER BY count DESC
""")

result.show()

# Complex query: average spending by country, joining transactions and users
result2 = spark.sql("""
    SELECT 
        u.geo_data.country AS country,
        COUNT(DISTINCT u.user_id) AS user_count,
        COUNT(t.transaction_id) AS transaction_count,
        ROUND(AVG(t.total), 2) AS avg_transaction_value,
        ROUND(SUM(t.total), 2) AS total_revenue
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    GROUP BY u.geo_data.country
    ORDER BY total_revenue DESC
""")

result2.show(20)

spark.stop()
