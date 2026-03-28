import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعداد واجهة الصفحة
st.set_page_config(page_title="Accudent AI", page_icon="🦷")
st.title("🦷 Accudent AI - مساعد طبيب الأسنان")
st.write("قم برفع صورة الأشعة لتحليل القنوات وحساب القياسات بدقة.")

# مكان وضع الـ API Key (يفضل وضعه في Secrets لاحقاً)
api_key = st.sidebar.text_input("ادخل مفتاح Gemini API الخاص بك:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    uploaded_file = st.file_uploader("اختر صورة أشعة (X-ray)...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='الأشعة المرفوعة', use_column_width=True)
        
        if st.button('بدء التحليل'):
            with st.spinner('جاري تحليل القنوات...'):
                # إرسال الصورة للموديل
                response = model.generate_content(["قم بتحليل هذه الأشعة السنية، حدد القنوات بدقة واقترح قياسات تقريبية للطول.", image])
                st.subheader("نتائج التحليل:")
                st.write(response.text)
else:
    st.warning("رجاءً ادخل الـ API Key في الشريط الجانبي لتفعيل البرنامج.")
