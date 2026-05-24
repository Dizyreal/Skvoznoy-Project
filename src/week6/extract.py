# src/week6/extract.py
import json
import requests
import yaml
from pathlib import Path
from datetime import datetime, timedelta

def extract(config_path, output_dir):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    api_config = config['api']
    params = api_config['params'].copy()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    params['starttime'] = start_date.strftime('%Y-%m-%d')
    params['endtime'] = end_date.strftime('%Y-%m-%d')
    
    response = requests.get(api_config['base_url'], params=params, timeout=30)
    response.raise_for_status()
    
    output_path = Path(output_dir) / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2)
    
    return str(output_path)