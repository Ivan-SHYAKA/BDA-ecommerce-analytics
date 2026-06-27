from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ECommerceAnalytics") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.files.maxPartitionBytes", "32m") \
    .getOrCreate()

# Load transactions - multiline=True since it's a single JSON array
transactions = spark.read.option("multiline", "true").json("dataset/data/transactions.json")
print(f"Transactions loaded: {transactions.count():,}")
transactions.printSchema()

# Load products and users
products = spark.read.option("multiline", "true").json("dataset/data/products.json")
users = spark.read.option("multiline", "true").json("dataset/data/users.json")

print(f"Products loaded: {products.count():,}")
print(f"Users loaded: {users.count():,}")

# Load sessions - all 20 files at once using wildcard
sessions = spark.read.option("multiline", "true").json("dataset/data/sessions_*.json")
print(f"Sessions loaded: {sessions.count():,}")