# Distributed Multi-Model Analytics for E-commerce Data



Big Data Analytics Final Project — a multi-model analytics system for a simulated e-commerce platform, using MongoDB, HBase, and Apache Spark.



## Overview



This project analyzes 90 days of simulated e-commerce activity (10,000 users, 5,000 products, 25 categories, 500,000 transactions, and 2,000,000 browsing sessions) using three complementary database technologies, each suited to a different data shape and access pattern.



## Project Structure



├── dataset\_generator.py     # Generates the synthetic dataset



├── dataset/                 # Generated JSON files (not included - see Setup)



├── mongodb/                 # MongoDB loading scripts and aggregation pipelines



├── hbase/                   # HBase schema, loading, and query scripts



├── spark/                   # Spark batch processing, SQL queries, and integration analysis



├── visualizations/          # Chart generation script and output PNGs



├── results/                 # Exported analysis results (CSV)



└── report/                  # Full technical report (PDF)



## Setup Instructions



### 1. Generate the dataset

```bash

pip install faker pandas

python dataset\_generator.py

```

This produces `users.json`, `products.json`, `categories.json`, `transactions.json`, and 20 `sessions\_N.json` files inside `dataset/data/`.



### 2. MongoDB

Requires MongoDB Community Server installed and running locally on port 27017.

```bash

pip install pymongo

python mongodb/mongodb\_load.py

python mongodb/mongodb\_indexes.py

python mongodb/mongodb\_queries.py

```



### 3. HBase

Requires Docker. Start an HBase container:

```bash

docker run -d --name hbase-container -p 16000:16000 -p 16010:16010 -p 16020:16020 -p 16030:16030 -p 2181:2181 -p 9090:9090 -p 9095:9095 dajobe/hbase

docker exec -d hbase-container hbase thrift start

```

Then create the tables via the HBase shell:

```bash

docker exec -it hbase-container hbase shell

create 'user\_sessions', 'session\_info', 'device', 'activity'

create 'product\_metrics', 'product\_info', 'metrics'

```

Load and query data:

```bash

pip install happybase

python hbase/hbase\_load.py

python hbase/hbase\_queries.py

```



### 4. Apache Spark

Requires Java 17+ and Spark 3.5.8.

```bash

pip install pyspark==3.5.8

python spark/data\_quality\_check.py

python spark/spark\_affinity.py

python spark/spark\_cohort.py

python spark/spark\_sql\_queries.py

python spark/spark\_integration.py

```



### 5. Visualizations

```bash

pip install matplotlib seaborn

python visualizations/visualizations.py

```



## Key Findings



\- Top revenue product generated over $330,000 across the dataset

\- Users segmented into low/medium/high purchasing frequency groups (2,174 / 5,252 / 2,574)

\- Product pairs viewed together repeatedly show rising purchase conversion (7.5% → 12.5%)

\- Average transaction value is notably higher for bank transfer and gift card payments (\~$1,100) than other methods (\~$770-$935)



See `report/Technical\_Report.pdf` for the full analysis, methodology, and visualizations.



## Notes on Scope



Due to local hardware constraints (8GB RAM), Spark analysis was conducted on representative samples of session data rather than the full 2,000,000 records. This is documented in the Limitations section of the technical report.

