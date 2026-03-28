import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# إعداد الصفحة
st.set_page_config(page_title="Accudent AI - PRO Mode", page_icon="🦷")
st.title("🦷 Accudent AI: High-Precision PRO Analysis")

api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # إجبار البرنامج على استخدام PRO فقط
        # لو النسخة دي مش متاحة في حسابك هيطلع Error واضح بدل ما يشتغل غلط
        model = genai.GenerativeModel("gemini-1.5-pro")

        uploaded_file = st.file_uploader("ارفع صورة الأشعة للتحليل بنسخة PRO", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="X-ray Uploaded", use_container_width=True)

            if st.button("بدء التحليل الدقيق (Pro Mode) ✨"):
                with st.spinner("جاري التشغيل باستخدام أقوى محرك ذكاء اصطناعي..."):
                    
                    # برومبت صارم جداً
                    prompt = """
                    You are a world-class Endodontic Specialist and Radiologist.
                    Task: Measure the working length with 0.1mm precision.
                    Calibration: Use the white lines on the right (distance between 2 lines = 1.8mm).
                    Points: Measure from the K-file stopper to the anatomical root apex.
                    Analysis: Identify the tooth, canal condition, and any periapical lesions.
                    Output: Professional clinical report including the EXACT measurement in MM.
                    """
                    
                    response = model.generate_content([prompt, img])
                    
                    st.success("✅ تم التحليل بنسخة Pro")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"❌ خطأ في نسخة Pro: {e}")
        st.info("تأكد أن الـ API Key الخاص بك يدعم موديل gemini-1.5-pro من Google AI Studio.")
else:
    st.info("💡 أدخل المفتاح (API Key) للتشغيل بنسخة PRO.")
