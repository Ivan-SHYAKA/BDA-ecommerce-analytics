from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Pipeline 1: Top 10 products by revenue
print("Running Pipeline 1: Top 10 products by revenue...")

pipeline_1 = [
    {"$unwind": "$items"},
    {"$group": {
        "_id": "$items.product_id",
        "total_revenue": {"$sum": "$items.subtotal"},
        "total_units_sold": {"$sum": "$items.quantity"}
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
]

results = list(db.transactions.aggregate(pipeline_1))
for r in results:
    print(f"Product: {r['_id']} | Revenue: ${r['total_revenue']:,.2f} | Units: {r['total_units_sold']:,}")


# Pipeline 2: User segmentation by purchasing frequency
print("\nRunning Pipeline 2: User segmentation by purchasing frequency...")

pipeline_2 = [
    {"$group": {
        "_id": "$user_id",
        "transaction_count": {"$sum": 1}
    }},
    {"$addFields": {
        "segment": {
            "$switch": {
                "branches": [
                    {"case": {"$lt": ["$transaction_count", 45]}, "then": "low"},
                    {"case": {"$lt": ["$transaction_count", 55]}, "then": "medium"}
                ],
                "default": "high"
            }
        }
    }},
    {"$group": {
        "_id": "$segment",
        "user_count": {"$sum": 1},
        "avg_transactions": {"$avg": "$transaction_count"}
    }},
    {"$sort": {"user_count": -1}}
]

results = list(db.transactions.aggregate(pipeline_2))
for r in results:
    print(f"Segment: {r['_id']} | Users: {r['user_count']:,} | Avg transactions: {r['avg_transactions']:.1f}")


# Pipeline 3: Total revenue by category (with category names)
print("\nRunning Pipeline 3: Total revenue by category...")

pipeline_3 = [
    {"$unwind": "$items"},
    {"$lookup": {
        "from": "products",
        "localField": "items.product_id",
        "foreignField": "product_id",
        "as": "product_info"
    }},
    {"$unwind": "$product_info"},
    {"$lookup": {
        "from": "categories",
        "localField": "product_info.category_id",
        "foreignField": "category_id",
        "as": "category_info"
    }},
    {"$unwind": "$category_info"},
    {"$group": {
        "_id": {
            "category_id": "$product_info.category_id",
            "category_name": "$category_info.name"
        },
        "total_revenue": {"$sum": "$items.subtotal"},
        "total_orders": {"$sum": 1}
    }},
    {"$sort": {"total_revenue": -1}}
]

results = list(db.transactions.aggregate(pipeline_3))
for r in results:
    print(f"Category: {r['_id']['category_id']} | Name: {r['_id']['category_name']} | Revenue: ${r['total_revenue']:,.2f} | Orders: {r['total_orders']:,}")