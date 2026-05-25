import pandas as pd
import json
from pathlib import Path

def transform_period(config_path, period, mart_dir, regions_path):
    raw_path = Path(f"data/raw/variant_15/raw_{period}.json")
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    regions = pd.read_csv(regions_path)
    
    features = raw_data.get('features', [])
    records = []
    
    for eq in features:
        props = eq.get('properties', {})
        geometry = eq.get('geometry', {})
        coords = geometry.get('coordinates', [None, None, None])
        
        record = {
            'event_id': eq.get('id'),
            'magnitude': props.get('mag'),
            'place': props.get('place'),
            'time': pd.to_datetime(props.get('time'), unit='ms'),
            'latitude': coords[1],
            'longitude': coords[0],
            'depth_km': coords[2],
            'region_id': 'US_CA'
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df = df[df['magnitude'].notna()]
    df['date'] = df['time'].dt.date
    
    daily = df.groupby('date').agg(
        earthquake_count=('event_id', 'count'),
        avg_magnitude=('magnitude', 'mean'),
        max_magnitude=('magnitude', 'max'),
        avg_depth_km=('depth_km', 'mean')
    ).reset_index()
    
    daily['date'] = pd.to_datetime(daily['date'])
    daily['region_id'] = 'US_CA'
    daily = daily.merge(regions, on='region_id', how='left')
    
    output_path = Path(mart_dir) / f"mart_{period}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(output_path, index=False)
    
    return str(output_path), len(daily)