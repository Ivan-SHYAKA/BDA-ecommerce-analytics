from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TestSession").getOrCreate()
print("Spark session created successfully!")
print(f"Spark version: {spark.version}")

spark.stop()