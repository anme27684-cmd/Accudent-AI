import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعداد الصفحة
st.set_page_config(page_title="Accudent AI", page_icon="🦷", layout="centered")
st.title("🦷 Accudent AI: Smart Diagnostics")

# 2. إدخال المفتاح
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # ---------------------------------------------------------
        # الحل الجذري: كود بيبحث عن الموديل المتاح للـ API بتاعك تلقائياً
        # ---------------------------------------------------------
        available_model_name = None
        
        # البرنامج بيلف على كل الموديلات المتاحة في حسابك
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # بيدور على أي موديل بيدعم الصور (pro أو flash أو vision)
                if 'flash' in m.name or 'pro' in m.name or 'vision' in m.name:
                    available_model_name = m.name
                    break # أول ما يلاقيه، يمسك فيه ويوقف بحث
        
        # لو ملقاش أي موديل خالص
        if not available_model_name:
            st.error("❌ الـ API Key الخاص بك لا يدعم أي موديل حالياً. تأكد من تفعيل الحساب.")
            st.stop()
            
        # لو لقاه، هيكتب لك اسمه عشان تتطمن
        st.sidebar.success(f"✅ متصل بنجاح: {available_model_name}")
        
        # 3. تشغيل الموديل اللي لاقاه
        model = genai.GenerativeModel(available_model_name)

        # 4. رفع الصورة والتحليل
        uploaded_file = st.file_uploader("ارفع صورة الأشعة (JPG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="الأشعة المرفوعة", use_container_width=True)

            if st.button("بدء التحليل ✨"):
                with st.spinner("جاري التحليل..."):
                    prompt = """
                    You are an expert dental radiologist. Analyze this X-ray:
                    1. Identify visible teeth.
                    2. Evaluate root canals.
                    3. Note any radiolucency or caries.
                    Be concise and professional.
                    """
                    response = model.generate_content([prompt, image])
                    
                    st.success("تم التحليل بنجاح!")
                    st.write(response.text)

    except Exception as e:
        st.error("❌ حدث خطأ في الاتصال:")
        st.code(str(e))
else:
    st.info("💡 أدخل المفتاح (API Key) في القائمة الجانبية للبدء.")
