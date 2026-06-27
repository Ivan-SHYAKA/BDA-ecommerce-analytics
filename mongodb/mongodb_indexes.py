from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Indexes for each collection
db.users.create_index("user_id", unique=True)
db.products.create_index("product_id", unique=True)
db.products.create_index("category_id")
db.transactions.create_index("user_id")
db.transactions.create_index("timestamp")
db.sessions.create_index("user_id")
db.sessions.create_index("session_id")
db.sessions.create_index("start_time")

print("All indexes created successfully.")