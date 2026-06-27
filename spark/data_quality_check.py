from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

spark = SparkSession.builder \
    .appName("DataQualityCheck") \
    .config("spark.driver.memory", "3g") \
    .config("spark.sql.files.maxPartitionBytes", "4m") \
    .getOrCreate()

transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")
print("Null counts in transactions:")
transactions.select([count(when(col(c).isNull(), c)).alias(c) for c in transactions.columns]).show()

# Only 1 session file this time, and drop heavy nested columns immediately
sessions = spark.read.option("multiline", "true").json("dataset/data/sessions_0.json")
sessions_light = sessions.drop("page_views", "cart_contents", "viewed_products")

print(f"Sessions loaded (sample): {sessions_light.count():,}")
print("Null counts in sessions (lightweight columns only):")
sessions_light.select([count(when(col(c).isNull(), c)).alias(c) for c in sessions_light.columns]).show()

spark.stop()