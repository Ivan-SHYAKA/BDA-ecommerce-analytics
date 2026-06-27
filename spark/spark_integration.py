from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, count

spark = SparkSession.builder \
    .appName("ProductAffinityIntegration") \
    .config("spark.driver.memory", "3g") \
    .getOrCreate()

# Load only 1 session file (lightweight - just what we need)
sessions = spark.read.option("multiline", "true").json("dataset/data/sessions_0.json")
sessions_light = sessions.select("session_id", "viewed_products")

# Step 1: explode viewed_products array
viewed_exploded = sessions_light.select(
    "session_id", 
    explode("viewed_products").alias("product_id")
)

viewed_exploded.show(10)
print(f"Total exploded view rows: {viewed_exploded.count():,}")

# Step 2: self-join to get viewed-together pairs
view_a = viewed_exploded.alias("a")
view_b = viewed_exploded.alias("b")

view_pairs = view_a.join(view_b,
    (col("a.session_id") == col("b.session_id")) &
    (col("a.product_id") < col("b.product_id"))
).select(
    col("a.product_id").alias("product_1"),
    col("b.product_id").alias("product_2")
)

# Count how often each pair was viewed together
view_pair_counts = view_pairs.groupBy("product_1", "product_2") \
    .agg(count("*").alias("times_viewed_together")) \
    .orderBy(col("times_viewed_together").desc())

view_pair_counts.show(10)

# Reload transaction pairs (from earlier analysis)
transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")
items_exploded = transactions.select("transaction_id", explode("items").alias("item")) \
    .select("transaction_id", col("item.product_id").alias("product_id"))

items_a = items_exploded.alias("ia")
items_b = items_exploded.alias("ib")

purchase_pairs = items_a.join(items_b,
    (col("ia.transaction_id") == col("ib.transaction_id")) &
    (col("ia.product_id") < col("ib.product_id"))
).select(
    col("ia.product_id").alias("product_1"),
    col("ib.product_id").alias("product_2")
)

purchase_pair_counts = purchase_pairs.groupBy("product_1", "product_2") \
    .agg(count("*").alias("times_bought_together"))

# INTEGRATION: join viewed-together with bought-together
integrated = view_pair_counts.join(
    purchase_pair_counts,
    ["product_1", "product_2"],
    "left"
).fillna(0, subset=["times_bought_together"])

integrated.orderBy(col("times_viewed_together").desc()).show(20)

# Export full results to CSV for visualization
integrated_pandas = integrated.toPandas()
integrated_pandas.to_csv("integration_results.csv", index=False)
print(f"Exported {len(integrated_pandas):,} pairs to CSV")

spark.stop()