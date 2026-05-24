# src/week6/transform.py
import pandas as pd
import json
from pathlib import Path

def transform(raw_path, mart_dir, regions_path):
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
            'mag_type': props.get('magType'),
            'place': props.get('place'),
            'time': pd.to_datetime(props.get('time'), unit='ms'),
            'updated': pd.to_datetime(props.get('updated'), unit='ms'),
            'felt': props.get('felt', 0),
            'tsunami': props.get('tsunami', 0),
            'latitude': coords[1],
            'longitude': coords[0],
            'depth_km': coords[2],
            'region_id': 'US_CA'
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    df['magnitude'] = pd.to_numeric(df['magnitude'], errors='coerce')
    df['depth_km'] = pd.to_numeric(df['depth_km'], errors='coerce')
    df['felt'] = pd.to_numeric(df['felt'], errors='coerce').fillna(0)
    df['tsunami'] = pd.to_numeric(df['tsunami'], errors='coerce').fillna(0)
    
    df = df[df['magnitude'].notna()]
    
    df['date'] = df['time'].dt.date
    
    df = df.merge(regions, on='region_id', how='left')
    
    daily = df.groupby('date').agg(
        earthquake_count=('event_id', 'count'),
        avg_magnitude=('magnitude', 'mean'),
        max_magnitude=('magnitude', 'max'),
        min_magnitude=('magnitude', 'min'),
        avg_depth_km=('depth_km', 'mean'),
        max_depth_km=('depth_km', 'max')
    ).reset_index()
    
    daily['date'] = pd.to_datetime(daily['date'])
    
    daily['avg_magnitude_7d'] = daily['avg_magnitude'].rolling(window=7, min_periods=1).mean()
    daily['earthquake_count_7d'] = daily['earthquake_count'].rolling(window=7, min_periods=1).sum()
    
    daily['deep_events_count'] = df.groupby('date').apply(
        lambda x: (x['depth_km'] > 70).sum()
    ).reset_index(drop=True)
    
    daily['deep_events_pct'] = (daily['deep_events_count'] / daily['earthquake_count'] * 100).round(1)
    
    daily['year'] = daily['date'].dt.year
    daily['month'] = daily['date'].dt.month
    daily['week'] = daily['date'].dt.isocalendar().week
    daily['day_of_week'] = daily['date'].dt.dayofweek
    
    daily['region_id'] = 'US_CA'
    daily['region_name'] = regions.loc[regions['region_id'] == 'US_CA', 'region_name'].values[0]
    
    output_path = Path(mart_dir) / f"{Path(raw_path).stem}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(output_path, index=False)
    
    return str(output_path), daily['date'].max()