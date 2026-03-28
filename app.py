import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="AccuDent AI - Dr. Ahmed Mode", page_icon="🦷")

st.title("🦷 AccuDent AI: Pro Vision")

api_key = st.sidebar.text_input("🔑 Enter your API Key:", type="password")

# التعليمات دي بتخلي الموديل يتقمص شخصيتك ويعرف إنه بيكلم دكتور زميل
SYSTEM_BEHAVIOR = """
You are now acting as the internal engine for Dr. Ahmed Rashad's AccuDent AI.
Dr. Ahmed is a dental intern and researcher. When he sends you an X-ray:
1. Treat him as a colleague.
2. Calibration: The white scale on the right has intervals of 1.8mm.
3. Be surgical in your precision. 
4. Always provide the working length from the stopper to the apex.
5. Do not say 'As an AI', instead say 'Based on our AccuDent analysis'.
"""

if api_key:
    try:
        genai.configure(api_key=api_key)
        # استدعاء النسخة اللي ظاهرة عندك في الصورة
        model = genai.GenerativeModel(
            model_name="gemini-3-pro",
            system_instruction=SYSTEM_BEHAVIOR
        )

        uploaded_file = st.file_uploader("ارفع الأشعة يا دكتور...", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True)

            if st.button("بدء التحليل الاحترافي 🚀"):
                with st.spinner("جاري التواصل مع المحرك الرئيسي..."):
                    # إرسال الصورة مع طلب الدردشة
                    response = model.generate_content(["Please analyze this X-ray as we discussed in our private protocol.", img])
                    st.success("النتيجة:")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("جرب تغيير الاسم لـ 'gemini-1.5-pro' إذا استمر الخطأ.")
else:
    st.info("أدخل الـ Key لتفعيل نمط التقمص.")
