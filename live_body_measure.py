# live_body_measure.py
# Simple local test runner that shows detection, clothing selection and measurements on screen.
import cv2
from camera_module import init_pose, get_landmarks_from_frame
from measurement_module import analyze_frame
from clothing_selector import decide_clothing_type, clothing_summary

# default mediapipe settings
pose = init_pose(static_image_mode=False, model_complexity=1,
                 enable_segmentation=False, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5)

selected_clothing = "Auto"  # default to auto
known_height_cm = 170  # default; adjust via keyboard if you want

def draw_ui(frame, selected):
    cv2.putText(frame, f"Selected: {selected}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    cv2.putText(frame, "Keys: 1-Shirt 2-Pant 3-Kurta 4-Jacket 5-FullSet 6-Auto 7-IncHeight 8-DecHeight Q-Quit", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

def main():
    global selected_clothing, known_height_cm
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam (index 0). Try other camera index or allow permission.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (960, 540))
        landmarks, annotated = get_landmarks_from_frame(frame, pose)
        draw_ui(annotated, selected_clothing)

        analysis = analyze_frame(landmarks, known_height_cm)

        status = analysis.get('status')
        full = analysis.get('full_body', False)
        measurements = analysis.get('measurements', {})

        cv2.putText(annotated, f"Status: {status}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 1)
        cv2.putText(annotated, f"Full body: {full}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 1)
        if analysis.get('px_per_cm'):
            cv2.putText(annotated, f"px/cm: {analysis['px_per_cm']}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 1)

        effective = decide_clothing_type(selected_clothing, full)
        summary = clothing_summary(measurements or {}, effective)
        # draw summary on right
        x0 = 600
        y0 = 90
        for line in summary.splitlines():
            cv2.putText(annotated, line, (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            y0 += 25

        cv2.imshow("Live Body Measure (press Q to quit)", annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            selected_clothing = "Shirt"
        elif key == ord('2'):
            selected_clothing = "Pant"
        elif key == ord('3'):
            selected_clothing = "Kurta"
        elif key == ord('4'):
            selected_clothing = "Jacket"
        elif key == ord('5'):
            selected_clothing = "Full Set (Shirt + Pant)"
        elif key == ord('6'):
            selected_clothing = "Auto"
        elif key == ord('7'):
            known_height_cm += 1
            print("Height increased:", known_height_cm)
        elif key == ord('8'):
            known_height_cm -= 1
            print("Height decreased:", known_height_cm)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
