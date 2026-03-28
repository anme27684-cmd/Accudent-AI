import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import numpy as np
import cv2
import json
import re

# 1. إعداد الصفحة
st.set_page_config(page_title="Accudent AI - Visual Measurement", page_icon="🦷", layout="centered")
st.title("🦷 Accudent AI: Visual Measurement Confirmation")

# 2. إدخال المفتاح
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
MM_PER_LINE_GAP = 1.8

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # البحث عن الموديل
        available_model_name = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    available_model_name = m.name
                    break
        
        model = genai.GenerativeModel(available_model_name)

        # 3. رفع الصورة
        uploaded_file = st.file_uploader("ارفع صورة الأشعة", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            # عرض الصورة الأصلية
            img_orig = Image.open(uploaded_file).convert("RGB")
            st.image(img_orig, caption="Original X-ray", use_container_width=True)
            
            user_req = st.text_input("حدد نقاط القياس (مثلاً: من الـ Stopper للـ Apex):", "Measure from file stopper to root apex")

            if st.button("بدء التحليل والرسم ✨"):
                with st.spinner("جاري تحديد النقاط ورسم الخطوط..."):
                    
                    # الـ Prompt لطلب الإحداثيات
                    prompt = f"""
                    Identify the (x, y) pixel coordinates for:
                    1. Two adjacent calibration lines (1.8mm apart).
                    2. The {user_req}.
                    Return ONLY a JSON:
                    {{
                        "calib1": [x, y],
                        "calib2": [x, y],
                        "start": [x, y],
                        "end": [x, y]
                    }}
                    """
                    
                    response = model.generate_content([prompt, img_orig])
                    
                    try:
                        # استخراج الإحداثيات
                        coords = json.loads(re.search(r'\{.*\}', response.text, re.DOTALL).group(0))
                        
                        # حساب القياس رياضياً
                        p1, p2 = np.array(coords["calib1"]), np.array(coords["calib2"])
                        s, e = np.array(coords["start"]), np.array(coords["end"])
                        
                        pixels_per_mm = np.linalg.norm(p1 - p2) / MM_PER_LINE_GAP
                        final_mm = np.linalg.norm(s - e) / pixels_per_mm
                        
                        # --- مرحلة الرسم (Visual Confirmation) ---
                        draw_img = img_orig.copy()
                        draw = ImageDraw.Draw(draw_img)
                        
                        # رسم نقط المعايرة (أخضر)
                        draw.ellipse([coords["calib1"][0]-5, coords["calib1"][1]-5, coords["calib1"][0]+5, coords["calib1"][1]+5], fill="green")
                        draw.ellipse([coords["calib2"][0]-5, coords["calib2"][1]-5, coords["calib2"][0]+5, coords["calib2"][1]+5], fill="green")
                        
                        # رسم خط القياس (أصفر) ونقط البداية والنهاية
                        draw.line([tuple(coords["start"]), tuple(coords["end"])], fill="yellow", width=3)
                        draw.ellipse([coords["start"][0]-8, coords["start"][1]-8, coords["start"][0]+8, coords["start"][1]+8], fill="red") # Stopper
                        draw.ellipse([coords["end"][0]-8, coords["end"][1]-8, coords["end"][0]+8, coords["end"][1]+8], fill="blue") # Apex
                        
                        # عرض النتيجة
                        st.subheader("✅ نتيجة القياس المرئية:")
                        st.image(draw_img, caption=f"Measurement: {final_mm:.2f} mm", use_container_width=True)
                        st.success(f"📏 الطول المقاس: {final_mm:.2f} mm")
                        st.write("🔴 نقطة البداية | 🔵 نقطة النهاية | 🟢 نقاط المعايرة")

                    except Exception as err:
                        st.error("لم يستطع الموديل تحديد النقاط بدقة، حاول مرة أخرى.")
                        st.write(response.text)

    except Exception as e:
        st.error(f"خطأ: {e}")
