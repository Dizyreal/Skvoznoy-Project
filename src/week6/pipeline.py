# src/week6/pipeline.py
import argparse
import json
from pathlib import Path
from datetime import datetime
from src.week6.extract import extract
from src.week6.transform import transform
from src.week6.load import load

STATE_PATH = Path("data/state/state.json")
CONFIG_PATH = Path("configs/variant_15.yml")
REGIONS_PATH = Path("reference/regions.csv")
MART_DIR = Path("data/mart")
TABLE_NAME = "mart_earthquakes_california"
DB_CONFIG = {
    "user": "analyst",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": "5432",
    "database": "earthquakes_db"
}

def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    return {"last_watermark": None, "last_run": None}

def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2, default=str)

def run_full():
    raw_path = extract(CONFIG_PATH, "data/raw/variant_15")
    mart_path, max_date = transform(raw_path, MART_DIR, REGIONS_PATH)
    row_count = load(mart_path, DB_CONFIG, TABLE_NAME, mode='replace')
    
    save_state({
        "last_watermark": str(max_date.date()),
        "last_run": datetime.now().isoformat(),
        "mode": "full"
    })

def run_incremental():
    state = load_state()
    raw_path = extract(CONFIG_PATH, "data/raw/variant_15")
    mart_path, max_date = transform(raw_path, MART_DIR, REGIONS_PATH)
    row_count = load(mart_path, DB_CONFIG, TABLE_NAME, mode='append')
    
    save_state({
        "last_watermark": str(max_date.date()),
        "last_run": datetime.now().isoformat(),
        "mode": "incremental"
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], required=True)
    args = parser.parse_args()
    
    if args.mode == "full":
        run_full()
    else:
        run_incremental()

if __name__ == "__main__":
    main()