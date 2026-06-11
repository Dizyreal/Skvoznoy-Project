#!/bin/bash
set -e

echo "[INIT] Creating airflow database if it does not exist..."

python3 - <<'PYEOF'
import psycopg2, time, sys

for i in range(30):
    try:
        conn = psycopg2.connect(
            host="postgres", user="student", password="student_pw", dbname="analytics"
        )
        break
    except Exception as e:
        if i == 29:
            print(f"[ERROR] Cannot connect to postgres: {e}")
            sys.exit(1)
        time.sleep(2)

conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = 'airflow'")
if not cur.fetchone():
    cur.execute("CREATE DATABASE airflow")
    print("[OK] Created database: airflow")
else:
    print("[OK] Database airflow already exists")

conn.close()
print("[OK] Database setup complete")
PYEOF

echo "[INIT] Running airflow db migrate..."
airflow db migrate

echo "[INIT] Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin 2>/dev/null || true

echo "[OK] Airflow initialization complete"
