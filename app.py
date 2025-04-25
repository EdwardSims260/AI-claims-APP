import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

# Use a lightweight YOLO model
MODEL_URL = "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"

@st.cache_resource
def load_model():
    from ultralytics import YOLO
    try:
        model = YOLO(MODEL_URL)
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

st.title("🚗 AI Damage Detector")
st.write("Upload a vehicle image for damage assessment")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with st.spinner("Analyzing..."):
        try:
            # Load image
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", use_column_width=True)
            
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Load model
            model = load_model()
            if model:
                # Run detection (focus on vehicles: car=2, truck=7, motorcycle=3)
                results = model.predict(img_cv, classes=[2, 3, 5, 7], conf=0.5)
                
                # Visualize results
                res_img = results[0].plot()
                res_img = cv2.cvtColor(res_img, cv2.COLOR_BGR2RGB)
                st.image(res_img, caption="Damage Detection", use_column_width=True)
                
                # Simple damage report
                damage_count = len(results[0].boxes)
                st.success(f"✅ Detected {damage_count} damage areas")
                st.warning(f"💶 Estimated repair cost: €{500 + damage_count * 200}")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Try a different image or check the console logs")
