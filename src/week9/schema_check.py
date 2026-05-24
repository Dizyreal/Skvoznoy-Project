import pandas as pd
import json
from pathlib import Path

EXPECTED_SCHEMA = {
    "date": "datetime64[ns]",
    "earthquake_count": "int64",
    "avg_magnitude": "float64",
    "max_magnitude": "float64",
    "min_magnitude": "float64",
    "avg_depth_km": "float64",
    "max_depth_km": "float64",
    "avg_magnitude_7d": "float64",
    "earthquake_count_7d": "float64",
    "deep_events_count": "int64",
    "deep_events_pct": "float64",
    "year": "int64",
    "month": "int64",
    "week": "int64",
    "day_of_week": "int64",
    "region_id": "object",
    "region_name": "object"
}

def check_schema_against_contract():
    mart_files = list(Path("data/mart").glob("*.csv"))
    if not mart_files:
        print("No mart files found")
        return False
    
    df = pd.read_csv(mart_files[0])
    df['date'] = pd.to_datetime(df['date'])
    
    missing = []
    for col in EXPECTED_SCHEMA:
        if col not in df.columns:
            missing.append(col)
    
    extra = []
    for col in df.columns:
        if col not in EXPECTED_SCHEMA and col not in ['time', 'updated', 'felt', 'tsunami']:
            extra.append(col)
    
    if missing:
        print(f"FAIL: Missing columns: {missing}")
    if extra:
        print(f"WARNING: Extra columns: {extra}")
    
    if not missing:
        print("PASS: Schema matches contract")
    
    return len(missing) == 0

if __name__ == "__main__":
    check_schema_against_contract()