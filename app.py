import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعداد الصفحة
st.set_page_config(page_title="Accudent AI", page_icon="🦷", layout="centered")

st.title("🦷 Accudent AI: Dental Analysis")
st.write("ارفع صورة الأشعة (X-ray) للتحليل الذكي")

# خلي الـ API Key في الجنب عشان الصفحة متعملش Refresh كل شوية
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)

        uploaded_file = st.file_uploader(
            "اختار صورة الأشعة (JPG, PNG)...",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="الحالة المرفوعة", use_container_width=True)

            if st.button("بدء التحليل ✨"):
                with st.spinner("جاري التحليل..."):
                    try:
                        # استعملنا Pro زي ما إنت طلبت لأنه أدق طبياً
                        model = genai.GenerativeModel("gemini-1.5-pro")

                        prompt = """
                        You are a professional dental radiologist.
                        Analyze this dental X-ray:
                        - Identify tooth/teeth shown.
                        - Evaluate root canal morphology and visibility.
                        - Detect any infection, radiolucency, or lesions.
                        - Identify restorations, fillings, or caries.
                        - Suggest the clinical next step (e.g., Endo, Extraction, Filling).
                        
                        Keep the answer short, clinical, and structured.
                        """

                        response = model.generate_content([prompt, image])

                        if response.text:
                            st.success("✅ تم التحليل بنجاح")
                            st.markdown(response.text)
                        else:
                            st.warning("⚠️ لم يتم استلام رد، حاول مرة أخرى.")

                    except Exception as e:
                        st.error("❌ حدث خطأ أثناء التحليل. تأكد من صلاحية الـ API Key.")
                        st.code(str(e))

    except Exception as e:
        st.error("❌ مشكلة في إعدادات الـ API")
        st.code(str(e))
else:
    st.info("💡 من فضلك أدخل الـ API Key من الشريط الجانبي لتفعيل البرنامج.")

st.markdown("---")
st.caption("Accudent AI - Smart Dental Diagnostics 🦷")
