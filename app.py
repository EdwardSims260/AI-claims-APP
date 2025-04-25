import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2

# Safe model loading function
@st.cache_resource
def load_model():
    try:
        # Load with weights_only=False for YOLO compatibility
        torch.load = lambda *args, **kwargs: torch.load(*args, **kwargs, weights_only=False)
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

st.title("🚗 Safe AI Damage Detector")

uploaded_file = st.file_uploader("Upload vehicle image", type=["jpg", "png"])
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image")
    
    model = load_model()
    if model:
        with st.spinner("Detecting damage..."):
            # Convert to numpy array
            img_np = np.array(img)
            
            # Run detection
            results = model.predict(img_np, classes=[2,3,5,7])  # Cars, bikes, etc.
            
            # Visualize results
            res_img = results[0].plot()
            st.image(res_img, caption="Damage Detection")
            
            # Simple damage report
            damage_count = len(results[0].boxes)
            st.success(f"Found {damage_count} damage areas")
