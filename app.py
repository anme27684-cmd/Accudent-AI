import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعداد واجهة البرنامج (AccuDent UI)
st.set_page_config(page_title="AccuDent AI - Pro Messenger", page_icon="🦷", layout="centered")

st.title("🦷 AccuDent AI: Pro Vision")
st.markdown("**أداة القياس الدقيق لعيادات الأسنان - نسخة السحابة (Cloud)**")

# 2. إدخال الـ API Key في القائمة الجانبية
api_key = st.sidebar.text_input("🔑 أدخل مفتاح Gemini API:", type="password")

# 3. التعليمات الصارمة (الرسالة اللي ساعي البريد بياخدها معاه)
INSTRUCTION = """
You are a highly precise Endodontic AI assistant. 
Task: Calculate the exact working length of the root canal from the provided X-ray.
Rules:
1. CALIBRATION: Find the white ruler lines on the right side of the image. The distance between ANY TWO adjacent white lines is EXACTLY 1.8 mm. Use this to calculate the pixels-per-mm ratio.
2. MEASUREMENT POINTS: Find the K-file's rubber stopper (start point) and the anatomical root apex (end point).
3. CALCULATION: Measure the pixel distance between the start and end points, then convert it to millimeters using your calibration ratio.
4. OUTPUT: Provide ONLY the final length in mm (e.g., '17.2 mm') followed by a 2-line clinical summary of the canal's condition. Do not guess. Do not use default averages.
"""

if api_key:
    try:
        # إعداد الاتصال بسيرفرات جوجل
        genai.configure(api_key=api_key)
        
        # استخدام العقل المدبر (Pro) لضمان الدقة الهندسية
        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        # 4. واجهة رفع الأشعة
        uploaded_file = st.file_uploader("📂 ارفع صورة الأشعة (JPG/PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="تم رفع الأشعة بنجاح، جاهزة للإرسال.", use_container_width=True)

            # 5. زر الإرسال والتحليل
            st.markdown("---")
            if st.button("🚀 تحليل وقياس (إرسال للـ Pro)"):
                with st.spinner("جاري إرسال البيانات وتحليل بكسلات الصورة في السيرفر..."):
                    
                    # الساعي بيبعت الرسالة + الصورة
                    response = model.generate_content([INSTRUCTION, img])
                    
                    # عرض النتيجة فور وصولها
                    st.success("✅ استلمت التقرير بنجاح!")
                    st.markdown("### 📋 النتيجة الطبية:")
                    st.info(response.text)

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء الاتصال: {e}")
        st.warning("تأكد إن الـ API Key صحيح ومفعل عليه موديل Pro.")
else:
    st.info("💡 لتبدأ، يرجى إدخال الـ API Key في القائمة الجانبية لتفعيل الاتصال.")
