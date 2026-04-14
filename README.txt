AI_AUTOMATED_FULLBODY_SIZE_SYSTEM

Files:
- main_app.py       : Streamlit app (UI)
- live_body_measure.py : Local OpenCV live test (keyboard controls)
- camera_module.py  : Mediapipe wrapper for frames + landmarks
- measurement_module.py : Pixel->cm calibration and measurement logic
- clothing_selector.py : Clothing selection + measurement filtering
- size_predictor.py : Zudio CSV-based size matching
- zudio_size_chart.py : helper to create sample CSV
- zudio_sizes.csv : (create this in project root, sample provided)
- requirements.txt  : Python dependencies

Run quick local test:
1. Create virtual env:
   python -m venv venv
   venv\\Scripts\\activate   (Windows)
   source venv/bin/activate  (macOS/Linux)
2. Install:
   pip install -r requirements.txt
3. Create sample Zudio CSV (optional):
   python -c "import zudio_size_chart as z; z.create_sample_csv()"
   (or create zudio_sizes.csv manually)
4. To test quickly with OpenCV:
   python live_body_measure.py
   - Use keys 1..6 to select clothing, q to quit.
5. To run the Streamlit UI:
   streamlit run main_app.py
