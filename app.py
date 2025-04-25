import streamlit as st
import cv2
import numpy as np
from PIL import Image
import random

# --- Streamlit App ---
st.set_page_config(page_title="AI Claims Estimator", page_icon="🚗")
st.title("🚗 AI Claims Estimator (MVP)")
st.write("Upload a photo of vehicle damage for instant repair cost estimation.")

# 1. Upload Image
uploaded_file = st.file_uploader("Upload Damage Photo", type=["jpg", "png"])

if uploaded_file:
    # 2. Display Image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Damage", use_column_width=True)

    # 3. Fake AI Analysis (Replace with DeepSeek Later)
    st.write("🔍 Analyzing damage...")

    # Simulate AI processing
    with st.spinner("Estimating repair cost..."):
        # Fake damage detection (replace with real model later)
        damage_types = ["Dent", "Scratch", "Cracked Headlight", "Paint Damage"]
        detected_damage = random.choice(damage_types)
        repair_cost = random.randint(200, 2000)  # Euros

    # 4. Show Results
    st.success(f"✅ Detected Damage: **{detected_damage}**")
    st.error(f"💶 Estimated Repair Cost: **€{repair_cost}**")

    # 5. Generate Fake "Claim Report"
    st.download_button(
        label="📄 Download Claim Report",
        data=f"Damage: {detected_damage}\nCost: €{repair_cost}",
        file_name="claim_report.txt",
    )
