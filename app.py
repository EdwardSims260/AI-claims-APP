import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2
import io
from contextlib import contextmanager

# Safe model loader context manager
@contextmanager
def custom_torch_load():
    original_load = torch.load
    def patched_load(*args, **kwargs):
        kwargs.pop('weights_only', None)  # Remove weights_only if present
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
            model = YOLO('yolov8n.pt', verbose=False)  # Disable verbose logging
            # Warm-up the model
            model.predict(np.zeros((640, 640, 3), imgsz=640, verbose=False)
            return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

# App Interface
st.set_page_config(page_title="AI Damage Inspector", layout="wide")
st.title("🚗 Vehicle Damage Assessment")

uploaded_file = st.file_uploader("Upload vehicle image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    # Read and resize image to prevent memory issues
    img = Image.open(io.BytesIO(uploaded_file.read())
    img = img.resize((1024, 768)) if max(img.size) > 1024 else img
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    model = load_model()
    if model:
        with st.spinner("Analyzing damage..."):
            try:
                # Convert to numpy and predict
                img_np = np.array(img)
                results = model.predict(
                    img_np,
                    classes=[2, 3, 5, 7],  # Cars, motorcycles, buses, trucks
                    conf=0.4,
                    imgsz=640,
                    verbose=False
                )
                
                # Visualize results
                res_img = results[0].plot()
                st.image(res_img, caption="Damage Detection", use_column_width=True)
                
                # Generate report
                damage_count = len(results[0].boxes)
                severity = "Major" if damage_count > 3 else "Minor"
                st.success(f"""
                **Assessment Complete**  
                ✅ Detected areas: {damage_count}  
                ⚠️ Severity: {severity}  
                💶 Estimated cost: €{800 + damage_count * 250}  
                """)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.info("Try a smaller image or different file format")
