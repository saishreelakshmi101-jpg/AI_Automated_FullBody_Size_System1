# size_predictor.py
# Simple zudio-style matcher using CSV file zudio_sizes.csv

import pandas as pd
from typing import Dict, Optional

def load_zudio(csv_path='zudio_sizes.csv'):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception:
        return None

def match_size(measurements: Dict[str, Optional[float]], df) -> Optional[Dict]:
    if measurements is None or df is None:
        return None
    best_score = float('inf')
    best_row = None
    for _, row in df.iterrows():
        score = 0.0
        if measurements.get('chest_cm') is not None and 'Chest_cm' in row:
            score += abs(row['Chest_cm'] - measurements['chest_cm']) * 3.0
        if measurements.get('waist_cm') is not None and 'Waist_cm' in row:
            score += abs(row['Waist_cm'] - measurements['waist_cm']) * 2.5
        if measurements.get('hip_cm') is not None and 'Hip_cm' in row:
            score += abs(row['Hip_cm'] - measurements['hip_cm']) * 1.5
        # height penalty if outside range
        if measurements.get('height_cm') is not None and 'HeightMin_cm' in row and 'HeightMax_cm' in row:
            h = measurements['height_cm']
            if not (row['HeightMin_cm'] <= h <= row['HeightMax_cm']):
                if h < row['HeightMin_cm']:
                    score += (row['HeightMin_cm'] - h) * 1.2
                else:
                    score += (h - row['HeightMax_cm']) * 1.2
        if score < best_score:
            best_score = score
            best_row = row
    if best_row is None:
        return None
    return {
        'Size': best_row['Size'],
        'Chest_cm': best_row.get('Chest_cm'),
        'Waist_cm': best_row.get('Waist_cm'),
        'Hip_cm': best_row.get('Hip_cm'),
        'HeightRange': f"{best_row.get('HeightMin_cm')}-{best_row.get('HeightMax_cm')}"
    }
