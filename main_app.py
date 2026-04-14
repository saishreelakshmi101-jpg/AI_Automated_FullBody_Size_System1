# main_app.py
# PREMIUM UI VERSION 🚀

import streamlit as st
import cv2
from camera_module import init_pose, get_landmarks_from_frame
from measurement_module import analyze_frame
from clothing_selector import decide_clothing_type, clothing_summary
from size_predictor import load_zudio, match_size
import time

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Clothing Size", layout="wide")

# -------------------- PREMIUM CSS --------------------
st.markdown("""
<style>

/* 🌈 Animated Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #a18cd1, #84fab0);
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* 🧊 Glass Card Effect */
.block-container {
    background: rgba(255, 255, 255, 0.15);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

/* ✨ Title Glow */
h1 {
    text-align: center;
    color: white;
    font-size: 40px;
    text-shadow: 0px 0px 15px rgba(255,255,255,0.8);
}

/* Text */
p, label, div {
    color: white;
    font-size: 15px;
}

/* 🔥 Buttons */
.stButton>button {
    background: linear-gradient(45deg, #ff512f, #dd2476);
    color: white;
    border-radius: 15px;
    padding: 12px 20px;
    font-size: 16px;
    border: none;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(45deg, #dd2476, #ff512f);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(#141e30, #243b55);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1>👕✨ AI Clothing Size Measurement ✨👖</h1>", unsafe_allow_html=True)

st.markdown("""
### 🤖 Smart AI that measures your body instantly  
📸 Stand straight in front of camera  
🛍️ Get perfect clothing size like magic
""")

# -------------------- ICONS --------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/892/892458.png", width=90)
    st.caption("👕 Shirts")

with c2:
    st.image("https://cdn-icons-png.flaticon.com/512/892/892462.png", width=90)
    st.caption("👖 Pants")

with c3:
    st.image("https://cdn-icons-png.flaticon.com/512/892/892461.png", width=90)
    st.caption("👗 Dresses")

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚙️ Settings")

camera_index = st.sidebar.number_input("📷 Camera", 0, 4, 0)
known_height = st.sidebar.number_input("📏 Height (cm)", 100, 230, 170)

model_complexity = st.sidebar.selectbox("🧠 Model (Fast=0)", [0,1,2], index=0)

min_det = st.sidebar.slider("🔍 Detection", 0.1, 0.99, 0.5)
min_track = st.sidebar.slider("🎯 Tracking", 0.1, 0.99, 0.5)

st.sidebar.markdown("---")

user_choice = st.sidebar.selectbox(
    "👗 Clothing",
    ['Auto','Shirt','Pant','Kurta','Jacket','Full Set']
)

# -------------------- DATA --------------------
zudio_df = load_zudio("zudio_sizes.csv")

# -------------------- LAYOUT --------------------
col1, col2 = st.columns([2,1])

frame_placeholder = col1.empty()
info_placeholder = col2.empty()
measure_placeholder = col2.empty()
size_placeholder = col2.empty()

# -------------------- POSE --------------------
pose = init_pose(
    static_image_mode=False,
    model_complexity=int(model_complexity),
    enable_segmentation=False,
    min_detection_confidence=float(min_det),
    min_tracking_confidence=float(min_track)
)

# -------------------- BUTTONS --------------------
b1, b2 = st.columns(2)
start = b1.button("🚀 Start")
stop = b2.button("🛑 Stop")

# -------------------- CAMERA LOOP --------------------
if start:
    cap = cv2.VideoCapture(int(camera_index))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        st.error("❌ Camera not working")
    else:
        st.success("📸 Camera Started")

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Frame error")
                break

            frame = cv2.resize(frame, (640, 480))

            landmarks, annotated = get_landmarks_from_frame(frame, pose)
            analysis = analyze_frame(landmarks, known_height)

            full = analysis.get('full_body', False)
            measure = analysis.get('measurements', {})
            status = analysis.get('status', 'no_data')

            frame_placeholder.image(
                cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                use_container_width=True
            )

            info_placeholder.markdown(f"""
### 📊 Status
**Status:** {status}  
**Full Body:** {full}
""")

            measure_placeholder.markdown("### 📏 Measurements")
            measure_placeholder.code(
                clothing_summary(
                    measure,
                    decide_clothing_type(user_choice, full)
                )
            )

            if zudio_df is not None and measure:
                matched = match_size(measure, zudio_df)
                if matched:
                    size_placeholder.markdown(f"""
### 🛍️ Recommended Size: **{matched['Size']}**

👕 Chest: {matched['Chest_cm']} cm  
📏 Waist: {matched['Waist_cm']} cm  
👖 Hip: {matched['Hip_cm']} cm
""")

            if stop:
                break

            time.sleep(0.01)

        cap.release()
        cv2.destroyAllWindows()
        st.success("✅ Stopped")

else:
    st.info("👉 Click START to begin")