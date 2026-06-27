from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, months_between, floor, avg, count as spark_count

spark = SparkSession.builder \
    .appName("CohortAnalysis") \
    .config("spark.driver.memory", "3g") \
    .getOrCreate()

users = spark.read.option("multiline", "true").json("dataset/data/users.json")

# Extract cohort month from registration_date
users_with_cohort = users.select(
    "user_id",
    "registration_date",
    date_format(col("registration_date"), "yyyy-MM").alias("cohort_month")
)

users_with_cohort.show(10)
users_with_cohort.groupBy("cohort_month").count().orderBy("cohort_month").show()

# Load transactions
transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")

# Join transactions with user cohort info
trans_with_cohort = transactions.join(users_with_cohort, "user_id") \
    .select(
        "user_id",
        "cohort_month",
        "registration_date",
        "timestamp",
        "total"
    )

# Calculate months since registration
trans_with_cohort = trans_with_cohort.withColumn(
    "months_since_registration",
    floor(months_between(col("timestamp"), col("registration_date")))
)

trans_with_cohort.show(10)

# Final cohort summary: average spending per cohort per month-since-registration
cohort_summary = trans_with_cohort.groupBy("cohort_month", "months_since_registration") \
    .agg(
        avg("total").alias("avg_spending"),
        spark_count("*").alias("transaction_count")
    ) \
    .orderBy("cohort_month", "months_since_registration")

cohort_summary.show(50)

spark.stop()