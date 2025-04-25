import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import tempfile
import os

# --- App Config ---
st.set_page_config(page_title="AI Insurance Claims", page_icon="🚗")
st.title("🚗 AI-Powered Damage Assessment")
st.write("Upload a photo of vehicle damage for instant analysis")

# --- Load YOLO Model (cached to avoid reloading) ---
@st.cache_resource
def load_model():
    try:
        model = YOLO("yolov8n.pt")  # Smallest model
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

model = load_model()

# --- Image Processing ---
def analyze_image(img):
    try:
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Run YOLO detection (focus on vehicles: car=2, truck=7, motorcycle=3)
        results = model.predict(img_cv, classes=[2, 3, 5, 7], conf=0.5)
        
        # Count damage areas (simplified - for demo)
        damage_count = sum(len(r.boxes) for r in results)
        
        # Visualize results
        annotated_img = results[0].plot()
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        
        return annotated_img, damage_count
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None, 0

# --- Main App ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with st.spinner("Analyzing damage..."):
        try:
            # Display original image
            img = Image.open(uploaded_file)
            st.image(img, caption="Original Image", use_column_width=True)
            
            # Process image
            annotated_img, damage_count = analyze_image(img)
            
            if annotated_img is not None:
                # Show results
                st.image(annotated_img, caption="Damage Detection", use_column_width=True)
                
                # Generate report
                st.success(f"✅ Detected {damage_count} damage areas")
                
                # Simple cost estimation
                base_cost = 500  # EUR
                total_cost = base_cost * (1 + damage_count * 0.5)
                st.warning(f"💶 Estimated repair cost: €{int(total_cost)}")
                
                # Download button
                report = f"""Damage Assessment Report:
- Detected Damage Areas: {damage_count}
- Estimated Repair Cost: €{int(total_cost)}
"""
                st.download_button(
                    label="📄 Download Report",
                    data=report,
                    file_name="damage_report.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

# --- Footer ---
st.markdown("---")
st.caption("""
This demo uses YOLOv8 for object detection. 
For accurate assessments, consult a professional.
""")
