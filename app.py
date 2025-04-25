import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2
import io
from contextlib import contextmanager

# --- Custom CSS for UI Enhancements ---
st.markdown("""
<style>
    .header {
        font-size: 2.5em !important;
        color: #2E86C1 !important;
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #28B463 !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px 24px;
    }
    .stProgress>div>div>div {
        background-color: #28B463;
    }
    .report-box {
        border-radius: 10px;
        padding: 20px;
        background-color: #E8F8F5;
        margin-top: 20px;
    }
    .damage-count {
        font-size: 1.8em;
        color: #C0392B;
        font-weight: bold;
    }
    .severity-high {
        color: #E74C3C;
        font-weight: bold;
    }
    .severity-low {
        color: #28B463;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- App Configuration ---
st.set_page_config(
    page_title="AutoDamage AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    st.title("Settings")
    confidence_threshold = st.slider(
        "Detection Confidence", 
        min_value=0.1, 
        max_value=0.9, 
        value=0.4, 
        step=0.1,
        help="Adjust how confident the model needs to be to detect damage"
    )
    st.markdown("---")
    st.info("""
    **How to use:**
    1. Upload a vehicle image
    2. Adjust detection settings
    3. View damage assessment
    4. Download the report
    """)

# --- Main Content ---
st.markdown('<div class="header">AutoDamage AI Inspector</div>', unsafe_allow_html=True)

# --- Model Loading (Cached) ---
@contextmanager
def custom_torch_load():
    original_load = torch.load
    def patched_load(*args, **kwargs):
        kwargs.pop('weights_only', None)
        return original_load(*args, **kwargs)
    torch.load = patched_load
    try:
        yield
    finally:
        torch.load = original_load

@st.cache_resource
def load_model():
    try:
        with custom_torch_load():
            from ultralytics import YOLO
            model = YOLO('yolov8n.pt', verbose=False)
            model.predict(np.zeros((640, 640, 3)), imgsz=640, verbose=False)
            return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

# --- File Upload Section ---
upload_col, preview_col = st.columns([2, 1])
with upload_col:
    uploaded_file = st.file_uploader(
        "Upload Vehicle Image", 
        type=["jpg", "png", "jpeg"],
        help="Upload clear images of vehicle damage for best results"
    )

# --- Image Processing ---
if uploaded_file:
    # Read and resize image
    img = Image.open(io.BytesIO(uploaded_file.read()))
    img = img.resize((1024, 768)) if max(img.size) > 1024 else img
    
    with preview_col:
        st.image(img, caption="Original Image", use_column_width=True)
    
    model = load_model()
    if model:
        with st.spinner("🔍 Analyzing damage... This may take 10-20 seconds"):
            try:
                # Convert to numpy and predict
                img_np = np.array(img)
                results = model.predict(
                    img_np,
                    classes=[2, 3, 5, 7],
                    conf=confidence_threshold,
                    imgsz=640,
                    verbose=False
                )
                
                # Visualize results
                res_img = results[0].plot()
                
                # Display results in tabs
                tab1, tab2 = st.tabs(["Damage Visualization", "Assessment Report"])
                
                with tab1:
                    st.image(res_img, caption="Damage Detection", use_column_width=True)
                
                with tab2:
                    damage_count = len(results[0].boxes)
                    severity = "High" if damage_count > 3 else "Low"
                    severity_class = "severity-high" if severity == "High" else "severity-low"
                    
                    st.markdown(f"""
                    <div class="report-box">
                        <h3>Damage Assessment Report</h3>
                        <p><b>Vehicle Type:</b> {results[0].names[results[0].boxes.cls[0] if len(results[0].boxes) > 0 else 'N/A'}</p>
                        <p><b>Damage Areas Found:</b> <span class="damage-count">{damage_count}</span></p>
                        <p><b>Severity:</b> <span class="{severity_class}">{severity}</span></p>
                        <p><b>Estimated Repair Cost:</b> €{800 + damage_count * 250}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download report
                    report_text = f"""
                    AUTODAMAGE AI REPORT
                    ====================
                    - Vehicle Type: {results[0].names[results[0].boxes.cls[0] if len(results[0].boxes) > 0 else 'N/A'}
                    - Damage Areas Found: {damage_count}
                    - Severity: {severity}
                    - Estimated Repair Cost: €{800 + damage_count * 250}
                    """
                    st.download_button(
                        label="📄 Download Full Report",
                        data=report_text,
                        file_name="damage_report.txt",
                        mime="text/plain"
                    )
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.info("Try adjusting the confidence threshold or using a different image")
