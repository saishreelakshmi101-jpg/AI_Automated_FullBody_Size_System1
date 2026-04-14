# clothing_selector.py
from typing import Dict, Optional

CLOTHING_REQUIREMENTS = {
    'Shirt': ['chest_cm', 'shoulder_cm', 'sleeve_cm', 'height_cm'],
    'Pant': ['waist_cm', 'hip_cm', 'inseam_cm', 'height_cm'],
    'Kurta': ['chest_cm', 'waist_cm', 'hip_cm', 'sleeve_cm', 'height_cm'],
    'Jacket': ['chest_cm', 'shoulder_cm', 'sleeve_cm', 'height_cm'],
    'Full Set (Shirt + Pant)': ['chest_cm', 'waist_cm', 'hip_cm', 'inseam_cm', 'sleeve_cm', 'height_cm']
}

def decide_clothing_type(user_choice: str, full_body_detected: bool) -> str:
    if user_choice == 'Auto':
        return 'Full Set (Shirt + Pant)' if full_body_detected else 'Shirt'
    return user_choice

def filter_measurements(measurements: Dict[str, Optional[float]], clothing_type: str) -> Dict[str, Optional[float]]:
    if not measurements:
        return {}
    keys = CLOTHING_REQUIREMENTS.get(clothing_type, [])
    return {k: measurements.get(k) for k in keys}

def clothing_summary(measurements: Dict[str, Optional[float]], clothing_type: str) -> str:
    sub = filter_measurements(measurements or {}, clothing_type)
    if not sub:
        return "Measurements not available yet."
    lines = []
    mapping = {
        'chest_cm': 'Chest',
        'shoulder_cm': 'Shoulder width',
        'sleeve_cm': 'Sleeve length',
        'waist_cm': 'Waist',
        'hip_cm': 'Hip',
        'inseam_cm': 'Inseam',
        'height_cm': 'Height'
    }
    for k, v in sub.items():
        label = mapping.get(k, k)
        lines.append(f"{label}: {'-' if v is None else str(v) + ' cm'}")
    return "\n".join(lines)
