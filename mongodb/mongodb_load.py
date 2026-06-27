import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Load categories
print("Loading categories...")
with open("dataset/data/categories.json", "r") as f:
    categories = json.load(f)
db.categories.drop()
db.categories.insert_many(categories)
print(f"Inserted {db.categories.count_documents({})} categories")

# Load products
print("Loading products...")
with open("dataset/data/products.json", "r") as f:
    products = json.load(f)
db.products.drop()
db.products.insert_many(products)
print(f"Inserted {db.products.count_documents({})} products")

# Load users
print("Loading users...")
with open("dataset/data/users.json", "r") as f:
    users = json.load(f)
db.users.drop()
db.users.insert_many(users)
print(f"Inserted {db.users.count_documents({})} users")

print("Done!")

# Load transactions
print("Loading transactions...")
with open("dataset/data/transactions.json", "r") as f:
    transactions = json.load(f)
db.transactions.drop()
db.transactions.insert_many(transactions)
print(f"Inserted {db.transactions.count_documents({})} transactions")

# Load sessions (20 files)
print("Loading sessions...")
db.sessions.drop()
total_sessions = 0

for i in range(20):
    print(f"  Loading sessions_{i}.json...")
    with open(f"dataset/data/sessions_{i}.json", "r") as f:
        sessions_chunk = json.load(f)
    db.sessions.insert_many(sessions_chunk)
    total_sessions += len(sessions_chunk)
    print(f"  Inserted {len(sessions_chunk)} sessions (total so far: {total_sessions:,})")

print(f"Done! Total sessions inserted: {total_sessions:,}")