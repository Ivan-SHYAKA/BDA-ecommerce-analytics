import json
import happybase
from collections import defaultdict

# Connect to HBase
connection = happybase.Connection('localhost', port=9090)

# ============================================
# PART 1: Load user_sessions
# ============================================
table_sessions = connection.table('user_sessions')

print("Loading sessions into HBase...")
count = 0

# Load only sessions_0.json as a representative subset
with open('dataset/data/sessions_0.json', 'r') as f:
    sessions = json.load(f)

batch = table_sessions.batch(batch_size=1000)

for session in sessions:
    row_key = f"{session['user_id']}#{session['start_time']}"
    
    batch.put(row_key.encode(), {
        b'session_info:session_id': str(session['session_id']).encode(),
        b'session_info:duration': str(session['duration_seconds']).encode(),
        b'session_info:conversion': str(session['conversion_status']).encode(),
        b'session_info:referrer': str(session['referrer']).encode(),
        b'device:type': str(session['device_profile']['type']).encode(),
        b'device:os': str(session['device_profile']['os']).encode(),
        b'device:browser': str(session['device_profile']['browser']).encode(),
        b'activity:viewed_products': str(len(session['viewed_products'])).encode(),
        b'activity:page_count': str(len(session['page_views'])).encode()
    })
    
    count += 1
    if count % 10000 == 0:
        print(f"Loaded {count:,} sessions...")

batch.send()
print(f"Done! Total sessions loaded: {count:,}")

# ============================================
# PART 2: Load product_metrics
# ============================================
table_products = connection.table('product_metrics')

print("\nLoading transactions to compute product metrics...")

with open('dataset/data/transactions.json', 'r') as f:
    transactions = json.load(f)

print(f"Loaded {len(transactions):,} transactions")

# Aggregate metrics per product per day
metrics = defaultdict(lambda: {"units_sold": 0, "revenue": 0.0, "order_count": 0})

for txn in transactions:
    date = txn["timestamp"][:10]  # extract YYYY-MM-DD
    for item in txn["items"]:
        product_id = item["product_id"]
        key = (product_id, date)
        metrics[key]["units_sold"] += item["quantity"]
        metrics[key]["revenue"] += item["subtotal"]
        metrics[key]["order_count"] += 1

print(f"Computed metrics for {len(metrics):,} product-date combinations")

batch2 = table_products.batch(batch_size=1000)
count2 = 0

for (product_id, date), m in metrics.items():
    row_key = f"{product_id}#{date}"
    
    batch2.put(row_key.encode(), {
        b'product_info:product_id': product_id.encode(),
        b'product_info:date': date.encode(),
        b'metrics:units_sold': str(m["units_sold"]).encode(),
        b'metrics:revenue': f"{m['revenue']:.2f}".encode(),
        b'metrics:order_count': str(m["order_count"]).encode()
    })
    
    count2 += 1
    if count2 % 5000 == 0:
        print(f"Loaded {count2:,} product-date records...")

batch2.send()
print(f"Done! Total product_metrics records loaded: {count2:,}")

connection.close()