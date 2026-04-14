# camera_module.py
# Optimized Webcam + MediaPipe Pose helper 🚀

import cv2
import mediapipe as mp

# Initialize mediapipe modules
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


def init_pose(static_image_mode=False, model_complexity=1, enable_segmentation=False,
              min_detection_confidence=0.5, min_tracking_confidence=0.5):
    """
    Initialize Mediapipe Pose safely (FIXED + OPTIMIZED)
    """

    return mp_pose.Pose(
        static_image_mode=bool(static_image_mode),

        # ✅ FIX: ensure correct types
        model_complexity=int(model_complexity),

        enable_segmentation=bool(enable_segmentation),

        min_detection_confidence=float(min_detection_confidence),
        min_tracking_confidence=float(min_tracking_confidence)
    )


def landmarks_to_pixel_dict(landmark_list, frame_w, frame_h):
    """
    Convert Mediapipe normalized landmarks to pixel coordinates
    """
    lm = {}

    for idx, l in enumerate(landmark_list.landmark):
        x = int(l.x * frame_w)
        y = int(l.y * frame_h)

        lm[idx] = (
            x,
            y,
            float(l.z),
            float(l.visibility)
        )

    return lm


def get_landmarks_from_frame(frame, pose):
    """
    Process frame and return:
    - landmarks dict
    - annotated frame
    """

    # 🚀 SPEED BOOST: mark frame non-writeable
    frame.flags.writeable = False

    # Convert to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process pose
    results = pose.process(frame_rgb)

    # Back to writeable
    frame.flags.writeable = True

    h, w = frame.shape[:2]
    landmarks = {}

    # Copy frame for drawing
    annotated = frame.copy()

    if results.pose_landmarks:
        landmarks = landmarks_to_pixel_dict(results.pose_landmarks, w, h)

        # 🎨 Better drawing (clean + fast)
        mp_draw.draw_landmarks(
            annotated,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2)
        )

    return landmarks, annotated