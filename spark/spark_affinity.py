from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, count

spark = SparkSession.builder \
    .appName("ProductAffinity") \
    .config("spark.driver.memory", "3g") \
    .getOrCreate()

transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")

# Step 1: explode the items array to get one row per (transaction_id, product_id)
items_exploded = transactions.select("transaction_id", explode("items").alias("item")) \
    .select("transaction_id", col("item.product_id").alias("product_id"))

items_exploded.show(10)
print(f"Total exploded rows: {items_exploded.count():,}")

# Step 2: self-join on transaction_id to get product pairs
items_a = items_exploded.alias("a")
items_b = items_exploded.alias("b")

pairs = items_a.join(items_b, 
    (col("a.transaction_id") == col("b.transaction_id")) & 
    (col("a.product_id") < col("b.product_id"))
).select(
    col("a.product_id").alias("product_1"),
    col("b.product_id").alias("product_2")
)

pairs.show(10)
print(f"Total pairs generated: {pairs.count():,}")

# Step 3: count how often each pair occurs
pair_counts = pairs.groupBy("product_1", "product_2") \
    .agg(count("*").alias("times_bought_together")) \
    .orderBy(col("times_bought_together").desc())

pair_counts.show(10)

spark.stop()