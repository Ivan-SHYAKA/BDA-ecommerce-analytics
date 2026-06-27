import happybase

connection = happybase.Connection('localhost', port=9090)
print("Connected to HBase!")
print("Tables:", connection.tables())
connection.close()