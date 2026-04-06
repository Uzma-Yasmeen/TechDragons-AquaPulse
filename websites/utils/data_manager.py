import os
import json
import random
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_FILE = os.path.join(DATA_DIR, 'buildings.json')

def load_or_generate_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if os.path.exists(DB_FILE):
        return pd.read_json(DB_FILE)
        
    # User requested exactly <=20 buildings with exactly 33/33/33 split.
    # 18 buildings gives exactly 6 of each.
    buildings = [f"Building {i}" for i in range(1, 19)]
    zones = ["North Ward", "South Ward", "East Ward", "West Ward"]
    
    # Pre-allocate exactly 33.3% to each status category
    statuses = ["Healthy"] * 6 + ["Needs Cleaning"] * 6 + ["Critical/Clogged"] * 6
    random.shuffle(statuses)
    
    data = []
    
    # Base coordinates for Chennai
    base_lat, base_lon = 13.0827, 80.2707
    
    for b, preset_status in zip(buildings, statuses):
        capacity = random.choice([5000, 10000, 15000])
        
        # Enforce strict compliance math based on preset
        if preset_status == "Healthy":
            efficiency = random.uniform(85.0, 100.0)
            months_since = random.randint(0, 2)
        elif preset_status == "Needs Cleaning":
            efficiency = random.uniform(40.0, 75.0)
            months_since = random.randint(3, 5)
        else: # Critical
            efficiency = random.uniform(5.0, 35.0)
            months_since = random.randint(6, 8)
            
        current_level = int((efficiency / 100) * capacity)
        
        # Random geographic spread across the city
        lat_offset = np.random.normal(0, 0.05)
        lon_offset = np.random.normal(0, 0.05)
        
        data.append({
            "Building": b,
            "Zone": random.choice(zones),
            "Lat": base_lat + lat_offset,
            "Lon": base_lon + lon_offset,
            "Capacity (L)": capacity,
            "Current Level (L)": current_level,
            "Efficiency (%)": round(efficiency, 1),
            "Status": preset_status,
            "Last Cleaned": f"{months_since} months ago"
        })
        
    df = pd.DataFrame(data)
    df.to_json(DB_FILE, orient='records', indent=4)
    return df
