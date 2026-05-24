import sys
from sqlalchemy import create_engine, text

DB_USER = "analyst"
DB_PASSWORD = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "earthquakes_db"
TABLE_NAME = "mart_earthquakes_california"

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

checks = [
    (
        "Check 1: Table is not empty", 
        f"SELECT COUNT(*) FROM {TABLE_NAME}", 
        lambda res: res[0][0] > 0 if res else False
    ),
    (
        "Check 2: Date range validation", 
        f"SELECT MIN(date), MAX(date) FROM {TABLE_NAME}", 
        lambda res: res[0][0] is not None if res else False
    ),
    (
        "Check 3: No NULLs in key columns", 
        f"""SELECT 
                SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) +
                SUM(CASE WHEN earthquake_count IS NULL THEN 1 ELSE 0 END) +
                SUM(CASE WHEN region_id IS NULL THEN 1 ELSE 0 END) +
                SUM(CASE WHEN region_name IS NULL THEN 1 ELSE 0 END)
            FROM {TABLE_NAME}""", 
        lambda res: res[0][0] == 0 if res else False
    ),
    (
        "Check 4: No duplicate dates per region", 
        f"SELECT date, region_id FROM {TABLE_NAME} GROUP BY date, region_id HAVING COUNT(*) > 1", 
        lambda res: len(res) == 0
    ),
    (
        "Check 5: Magnitude range validation", 
        f"SELECT MIN(avg_magnitude), MAX(max_magnitude) FROM {TABLE_NAME}", 
        lambda res: res[0][0] >= -2.0 and res[0][1] <= 10.0 if res and res[0][0] is not None else True
    ),
    (
        "Check 6: Earthquake count non-negative", 
        f"SELECT MIN(earthquake_count) FROM {TABLE_NAME}", 
        lambda res: res[0][0] >= 0 if res and res[0][0] is not None else True
    ),
    (
        "Check 7: Deep events percentage sanity", 
        f"SELECT MIN(deep_events_pct), MAX(deep_events_pct) FROM {TABLE_NAME} WHERE deep_events_pct IS NOT NULL", 
        lambda res: res[0][0] >= 0 and res[0][1] <= 100 if res and res[0][0] is not None else True
    ),
    (
        "Check 8: Rolling window sanity", 
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE earthquake_count_7d < earthquake_count", 
        lambda res: res[0][0] == 0 if res else False
    ),
    (
        "Check 9: Total earthquakes by month (No zero months)", 
        f"SELECT EXTRACT(MONTH FROM date) as m FROM {TABLE_NAME} GROUP BY m HAVING SUM(earthquake_count) = 0", 
        lambda res: len(res) == 0
    ),
    (
        "Check 10: Logical consistency of magnitudes", 
        f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE max_magnitude < avg_magnitude", 
        lambda res: res[0][0] == 0 if res else False
    )
]

def run_data_quality_checks():
    failed_checks = 0

    try:
        with engine.connect() as conn:
            for name, sql, validate_fn in checks:
                try:
                    result = conn.execute(text(sql)).fetchall()
                    if validate_fn(result):
                        print(f"PASSED: {name}")
                    else:
                        print(f"FAILED: {name}")
                        failed_checks += 1
                except Exception:
                    print(f"ERROR: {name}")
                    failed_checks += 1
    except Exception:
        sys.exit(1)

    if failed_checks == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_data_quality_checks()
