import happybase

connection = happybase.Connection('localhost', port=9090)
table = connection.table('user_sessions')

# Query: Get all sessions for a specific user
user_id = 'user_000042'
print(f"Sessions for {user_id}:")
print("-" * 60)

count = 0
for key, data in table.scan(row_prefix=user_id.encode()):
    print(f"Row key: {key.decode()}")
    print(f"  Device: {data[b'device:type'].decode()} | {data[b'device:os'].decode()}")
    print(f"  Duration: {data[b'session_info:duration'].decode()} seconds")
    print(f"  Conversion: {data[b'session_info:conversion'].decode()}")
    print(f"  Pages viewed: {data[b'activity:page_count'].decode()}")
    print()
    count += 1

print(f"Total sessions found: {count}")

# Query: Get all daily performance records for a specific product
product_id = 'prod_00154' # Product ID for which we want to retrieve daily performance metrics
table2 = connection.table('product_metrics')

print(f"\nDaily performance for {product_id}:")
print("-" * 60)

count2 = 0
total_units = 0
total_revenue = 0.0
total_orders = 0

for key, data in table2.scan(row_prefix=product_id.encode()):
    units = int(data[b'metrics:units_sold'].decode())
    revenue = float(data[b'metrics:revenue'].decode())
    orders = int(data[b'metrics:order_count'].decode())

    print(f"Row key: {key.decode()}")
    print(f"  Units sold: {units}")
    print(f"  Revenue: ${revenue:,.2f}")
    print(f"  Order count: {orders}")
    print()

    total_units += units
    total_revenue += revenue
    total_orders += orders
    count2 += 1

print("=" * 60)
print(f"SUMMARY for {product_id}")
print(f"Total days with sales: {count2}")
print(f"Total units sold: {total_units:,}")
print(f"Total revenue: ${total_revenue:,.2f}")
print(f"Total orders: {total_orders:,}")

connection.close()

