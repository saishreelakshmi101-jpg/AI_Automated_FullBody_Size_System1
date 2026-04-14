# measurement_module.py
# Pixel->cm calibration, half/full detection, and measurement computation.

import math
from typing import Dict, Tuple, Optional

# Mediapipe Pose landmark indices
LANDMARK = {
    'NOSE':0, 'LEFT_SHOULDER':11, 'RIGHT_SHOULDER':12,
    'LEFT_ELBOW':13, 'RIGHT_ELBOW':14, 'LEFT_WRIST':15, 'RIGHT_WRIST':16,
    'LEFT_HIP':23, 'RIGHT_HIP':24, 'LEFT_KNEE':25, 'RIGHT_KNEE':26,
    'LEFT_ANKLE':27, 'RIGHT_ANKLE':28
}

def euclid(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    return math.hypot(a[0]-b[0], a[1]-b[1])

def is_full_body_detected(landmarks: Dict[int, Tuple[int,int,float,float]]) -> bool:
    """
    Decide if full body is visible: require at least one ankle/knee visible with reasonable confidence.
    """
    if LANDMARK['LEFT_HIP'] not in landmarks or LANDMARK['RIGHT_HIP'] not in landmarks:
        return False
    knees = [i for i in (LANDMARK['LEFT_KNEE'], LANDMARK['RIGHT_KNEE']) if i in landmarks and landmarks[i][3] > 0.35]
    ankles = [i for i in (LANDMARK['LEFT_ANKLE'], LANDMARK['RIGHT_ANKLE']) if i in landmarks and landmarks[i][3] > 0.35]
    return bool(knees or ankles)

def calibrate_px_per_cm(landmarks: Dict[int, Tuple[int,int,float,float]], known_height_cm: float) -> Optional[float]:
    """
    Calibrate using pixel distance from nose -> ankle midpoint and the user's real height (cm).
    Returns px_per_cm (pixels per centimeter).
    """
    if LANDMARK['NOSE'] not in landmarks:
        return None
    nose = landmarks[LANDMARK['NOSE']][:2]
    ankles = [landmarks[i][:2] for i in (LANDMARK['LEFT_ANKLE',], LANDMARK['RIGHT_ANKLE']) if i in landmarks] \
             if False else None  # fallback to below (this avoids indexing problems)
    # compute available ankle points robustly
    ankles = []
    for idx in (LANDMARK['LEFT_ANKLE'], LANDMARK['RIGHT_ANKLE']):
        if idx in landmarks and landmarks[idx][3] > 0.2:
            ankles.append(landmarks[idx][:2])
    if not ankles:
        return None
    ankle_mid = (sum(p[0] for p in ankles)/len(ankles), sum(p[1] for p in ankles)/len(ankles))
    pixel_height = euclid(nose, ankle_mid)
    if pixel_height <= 5:
        return None
    return pixel_height / float(known_height_cm)

def compute_measurements(landmarks: Dict[int, Tuple[int,int,float,float]], px_per_cm: float) -> Dict[str, Optional[float]]:
    """
    Compute rough measurements (cm). Uses heuristics (not exact tailoring).
    Returns dict with shoulder_cm, chest_cm, waist_cm, hip_cm, sleeve_cm, inseam_cm, height_cm
    """
    meas = {'shoulder_cm': None, 'chest_cm': None, 'waist_cm': None, 'hip_cm': None,
            'sleeve_cm': None, 'inseam_cm': None, 'height_cm': None}

    try:
        if LANDMARK['LEFT_SHOULDER'] in landmarks and LANDMARK['RIGHT_SHOULDER'] in landmarks:
            l = landmarks[LANDMARK['LEFT_SHOULDER']][:2]
            r = landmarks[LANDMARK['RIGHT_SHOULDER']][:2]
            meas['shoulder_cm'] = round(euclid(l, r) / px_per_cm, 1)
    except Exception:
        pass

    try:
        # hip width
        if LANDMARK['LEFT_HIP'] in landmarks and LANDMARK['RIGHT_HIP'] in landmarks:
            l = landmarks[LANDMARK['LEFT_HIP']][:2]
            r = landmarks[LANDMARK['RIGHT_HIP']][:2]
            meas['hip_cm'] = round(euclid(l, r) / px_per_cm, 1)
    except Exception:
        pass

    # waist approx from hip
    if meas.get('hip_cm') is not None:
        meas['waist_cm'] = round(meas['hip_cm'] * 0.95, 1)

    # chest approx from shoulder width (empirical multiplier)
    if meas.get('shoulder_cm') is not None:
        meas['chest_cm'] = round(meas['shoulder_cm'] * 2.05, 1)

    # height (nose->ankle midpoint)
    try:
        if LANDMARK['NOSE'] in landmarks:
            nose = landmarks[LANDMARK['NOSE']][:2]
            ankles = [landmarks[i][:2] for i in (LANDMARK['LEFT_ANKLE'], LANDMARK['RIGHT_ANKLE']) if i in landmarks]
            if ankles:
                mid = (sum(p[0] for p in ankles)/len(ankles), sum(p[1] for p in ankles)/len(ankles))
                meas['height_cm'] = round(euclid(nose, mid) / px_per_cm, 1)
    except Exception:
        pass

    # inseam knee->ankle
    try:
        inseam_vals = []
        if LANDMARK['LEFT_KNEE'] in landmarks and LANDMARK['LEFT_ANKLE'] in landmarks:
            inseam_vals.append(euclid(landmarks[LANDMARK['LEFT_KNEE']][:2], landmarks[LANDMARK['LEFT_ANKLE']][:2]))
        if LANDMARK['RIGHT_KNEE'] in landmarks and LANDMARK['RIGHT_ANKLE'] in landmarks:
            inseam_vals.append(euclid(landmarks[LANDMARK['RIGHT_KNEE']][:2], landmarks[LANDMARK['RIGHT_ANKLE']][:2]))
        if inseam_vals:
            meas['inseam_cm'] = round((sum(inseam_vals)/len(inseam_vals)) / px_per_cm, 1)
    except Exception:
        pass

    # sleeve shoulder->wrist
    try:
        sleeve_vals = []
        if LANDMARK['LEFT_SHOULDER'] in landmarks and LANDMARK['LEFT_WRIST'] in landmarks:
            sleeve_vals.append(euclid(landmarks[LANDMARK['LEFT_SHOULDER']][:2], landmarks[LANDMARK['LEFT_WRIST']][:2]))
        if LANDMARK['RIGHT_SHOULDER'] in landmarks and LANDMARK['RIGHT_WRIST'] in landmarks:
            sleeve_vals.append(euclid(landmarks[LANDMARK['RIGHT_SHOULDER']][:2], landmarks[LANDMARK['RIGHT_WRIST']][:2]))
        if sleeve_vals:
            meas['sleeve_cm'] = round((sum(sleeve_vals)/len(sleeve_vals)) / px_per_cm, 1)
    except Exception:
        pass

    return meas

def analyze_frame(landmarks: Dict[int, Tuple[int,int,float,float]], known_height_cm: Optional[float]) -> Dict:
    """
    High-level helper for the app.
    Returns dict:
      full_body: bool
      px_per_cm: float or None
      measurements: dict or None
      status: string
    """
    result = {'full_body': False, 'px_per_cm': None, 'measurements': None, 'status': 'insufficient_landmarks'}
    if not landmarks or len(landmarks) < 4:
        result['status'] = 'insufficient_landmarks'
        return result
    full = is_full_body_detected(landmarks)
    result['full_body'] = full
    if known_height_cm is None:
        result['status'] = 'no_calibration'
        return result
    px_per_cm = calibrate_px_per_cm(landmarks, float(known_height_cm))
    if not px_per_cm:
        result['status'] = 'calibration_failed'
        return result
    result['px_per_cm'] = round(px_per_cm, 4)
    result['measurements'] = compute_measurements(landmarks, px_per_cm)
    result['status'] = 'ok'
    return result
