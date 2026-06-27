import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

sns.set_style("whitegrid")

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

# Chart 1: Top 10 products by revenue
pipeline_1 = [
    {"$unwind": "$items"},
    {"$group": {
        "_id": "$items.product_id",
        "total_revenue": {"$sum": "$items.subtotal"}
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
]

results = list(db.transactions.aggregate(pipeline_1))
products = [r["_id"] for r in results]
revenues = [r["total_revenue"] for r in results]

plt.figure(figsize=(10, 6))
plt.barh(products[::-1], revenues[::-1], color="steelblue")
plt.xlabel("Total Revenue ($)")
plt.title("Top 10 Products by Revenue")
plt.tight_layout()
plt.savefig("chart1_top_products.png", dpi=150)
print("Chart 1 saved!")
plt.close()

# Chart 2: User segmentation by purchasing frequency (with threshold ranges in labels)
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
        "user_count": {"$sum": 1}
    }}
]

results2 = list(db.transactions.aggregate(pipeline_2))
order = {"low": 0, "medium": 1, "high": 2}
results2.sort(key=lambda r: order[r["_id"]])

label_map = {
    "low": "Low\n(<45 transactions)",
    "medium": "Medium\n(45-54 transactions)",
    "high": "High\n(≥55 transactions)"
}

segments = [label_map[r["_id"]] for r in results2]
counts = [r["user_count"] for r in results2]

colors = {"Low\n(<45 transactions)": "#e74c3c",
          "Medium\n(45-54 transactions)": "#3498db",
          "High\n(≥55 transactions)": "#2ecc71"}
bar_colors = [colors[s] for s in segments]

plt.figure(figsize=(9, 6))
plt.bar(segments, counts, color=bar_colors)
plt.xlabel("Segment (by transaction count)")
plt.ylabel("Number of Users")
plt.title("User Segmentation by Purchasing Frequency")
for i, count in enumerate(counts):
    plt.text(i, count + 50, f"{count:,} users", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig("chart2_user_segments.png", dpi=150)
print("Chart 2 saved (updated)!")
plt.close()

# Chart 3: Revenue by payment method (from earlier Spark SQL results)
payment_methods = ["paypal", "credit_card", "apple_pay", "crypto", "bank_transfer", "gift_card"]
avg_totals = [932.05, 937.84, 767.41, 769.68, 1104.42, 1102.91]
counts3 = [125185, 125177, 64186, 64172, 60657, 60623]

fig, ax1 = plt.subplots(figsize=(10, 6))

x = range(len(payment_methods))
bars = ax1.bar(x, avg_totals, color="darkorange", alpha=0.8)
ax1.set_xlabel("Payment Method")
ax1.set_ylabel("Average Transaction Value ($)", color="darkorange")
ax1.set_xticks(x)
ax1.set_xticklabels(payment_methods, rotation=15)
ax1.set_title("Average Transaction Value by Payment Method")

for i, val in enumerate(avg_totals):
    ax1.text(i, val + 15, f"${val:,.0f}", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("chart3_payment_methods.png", dpi=150)
print("Chart 3 saved!")
plt.close()

# Chart 4: Viewed-together vs Bought-together (using full integration results)
import pandas as pd

integration_df = pd.read_csv("integration_results.csv")

# Group by times_viewed_together, calculate conversion stats
summary = integration_df.groupby("times_viewed_together").agg(
    pair_count=("product_1", "count"),
    avg_bought_together=("times_bought_together", "mean"),
    pct_ever_bought=("times_bought_together", lambda x: (x > 0).mean() * 100)
).reset_index()

print(summary)

fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.bar(summary["times_viewed_together"], summary["pair_count"], 
        color="lightsteelblue", alpha=0.7, label="Number of product pairs")
ax1.set_xlabel("Times Viewed Together (in same session)")
ax1.set_ylabel("Number of Product Pairs", color="steelblue")
ax1.set_yscale("log")

ax2 = ax1.twinx()
ax2.plot(summary["times_viewed_together"], summary["pct_ever_bought"], 
         color="red", marker="o", linewidth=2, label="% pairs ever bought together")
ax2.set_ylabel("% of Pairs Ever Bought Together", color="red")

plt.title("Product Pairs: View Frequency vs Purchase Conversion")
fig.tight_layout()
plt.savefig("chart4_view_vs_buy.png", dpi=150)
print("Chart 4 saved (improved)!")
plt.close()