import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعداد واجهة الصفحة
st.set_page_config(page_title="Accudent AI", page_icon="🦷")
st.title("🦷 Accudent AI - مساعد طبيب الأسنان")

# الشريط الجانبي للـ API Key
api_key = st.sidebar.text_input("ادخل مفتاح Gemini API الخاص بك:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # تحديث اسم الموديل للنسخة المستقرة
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_file = st.file_uploader("اختر صورة أشعة (X-ray)...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='الأشعة المرفوعة', use_container_width=True)
            
            if st.button('بدء التحليل'):
                with st.spinner('جاري تحليل القنوات...'):
                    # إرسال الصورة للموديل مع نص توضيحي
                    response = model.generate_content([
                        "تحليل طبي متخصص: قم بفحص صورة الأشعة السنية هذه، حدد القنوات بدقة، واقترح طول القناة التقريبي بالمليمتر.", 
                        image
                    ])
                    st.subheader("نتائج التحليل:")
                    st.markdown(response.text)
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال بجوجل: {e}")
else:
    st.info("💡 من فضلك ادخل الـ API Key في الشريط الجانبي لبدء العمل.")
