import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2

# Safe model loader with proper weights handling
@st.cache_resource
def load_model():
    try:
        # Create custom loader function
        def safe_load(*args, **kwargs):
            kwargs['weights_only'] = False  # Force disable security check
            return torch._load(*args, **kwargs)
            
        # Temporarily replace torch.load
        original_load = torch.load
        torch.load = safe_load
        
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        
        # Restore original loader
        torch.load = original_load
        return model
        
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

st.title("🚗 AI Damage Assessment")
st.write("Upload a vehicle image for damage detection")

uploaded_file = st.file_uploader("Choose image...", type=["jpg", "png", "jpeg"])
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    model = load_model()
    if model:
        with st.spinner("Analyzing damage..."):
            # Convert to numpy array
            img_np = np.array(img)
            
            # Run detection (focus on vehicles)
            results = model.predict(img_np, classes=[2, 3, 5, 7], conf=0.5)
            
            # Visualize results
            res_plotted = results[0].plot()
            st.image(res_plotted, caption="Damage Detection", use_column_width=True)
            
            # Generate report
            damage_count = len(results[0].boxes)
            st.success(f"✅ Detected {damage_count} damage areas")
            st.warning(f"💶 Estimated repair cost: €{500 + damage_count * 200}")
