import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5433"),
    dbname=os.getenv("DB_NAME", "ecommerce_test_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
)
conn.autocommit = True
cur = conn.cursor()

with open("db/schema.sql") as f:
    cur.execute(f.read())

with open("db/seed_data.sql") as f:
    cur.execute(f.read())

cur.close()
conn.close()
print("Schema and seed data loaded successfully")