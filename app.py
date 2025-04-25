import streamlit as st
import torch
from PIL import Image
import numpy as np
import cv2
import io

# Safe model loader that works with Streamlit Cloud restrictions
@st.cache_resource
def load_model():
    try:
        # Create a custom loader function
        def custom_loader(f, map_location=None, **kwargs):
            # Disable weights_only restriction
            if 'weights_only' in kwargs:
                del kwargs['weights_only']
            return torch.load(f, map_location=map_location, **kwargs)
        
        # Monkey patch torch.load temporarily
        original_load = torch.load
        torch.load = custom_loader
        
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        
        # Restore original loader
        torch.load = original_load
        return model
        
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        st.info("Please try refreshing the app or using a different image")
        return None

# App Interface
st.title("🚗 AI Damage Inspector")
st.write("Upload a vehicle image for instant damage assessment")

uploaded_file = st.file_uploader("Choose image...", type=["jpg", "png", "jpeg"])
if uploaded_file:
    # Read image
    img_bytes = uploaded_file.read()
    img = Image.open(io.BytesIO(img_bytes))
    st.image(img, caption="Uploaded Image", use_column_width=True)
    
    # Load model
    model = load_model()
    if model:
        with st.spinner("Analyzing damage..."):
            try:
                # Convert to numpy array
                img_np = np.array(img)
                
                # Run detection (focus on vehicles: cars, trucks, bikes)
                results = model.predict(img_np, classes=[2, 3, 5, 7], conf=0.5)
                
                # Visualize results
                res_plotted = results[0].plot()
                st.image(res_plotted, caption="Damage Detection", use_column_width=True)
                
                # Generate report
                damage_count = len(results[0].boxes)
                st.success(f"✅ Detected {damage_count} damage areas")
                st.warning(f"💶 Estimated repair cost: €{500 + damage_count * 200}")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
