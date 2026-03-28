import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعداد الصفحة
st.set_page_config(page_title="Accudent AI - Measurements", page_icon="🦷", layout="centered")
st.title("🦷 Accudent AI: Smart Diagnostics & Measurements")

# 2. إدخال المفتاح (في الجنب)
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# 3. ثابت المعايرة (Scale Definition)
# هذا السطر ثابت في الكود لإخبار النموذج بالقيمة الحقيقية بين الخطوط
MM_PER_LINE_GAP = 1.8

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # كود البحث عن الموديل المتاح تلقائياً (كما في الحل السابق)
        available_model_name = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name or 'vision' in m.name:
                    available_model_name = m.name
                    break
        
        if not available_model_name:
            st.error("❌ الـ API Key الخاص بك لا يدعم أي موديل حالياً.")
            st.stop()
            
        st.sidebar.success(f"✅ متصل بنجاح: {available_model_name}")
        model = genai.GenerativeModel(available_model_name)

        # 4. رفع الصورة
        uploaded_file = st.file_uploader("ارفع صورة الأشعة (JPG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="الأشعة المرفوعة", use_container_width=True)

            # ---------------------------------------------------------
            # 🆕 الميزة الجديدة: خانة إدخال للدكتور لتحديد نقاط القياس 🆕
            # ---------------------------------------------------------
            st.markdown("---")
            st.subheader("📍 طلب القياس المخصص (اختياري)")
            st.write("اكتب هنا نقاط القياس التي تريدها بالظبط (مثال: قس لي من حدبة السن (Cusp) إلى ذروة الجذر (Apex) لقناة MB)")
            
            # الدكتور بيكتب هنا
            user_measurement_request = st.text_input("ادخل طلب القياس الخاص بك:")

            # ---------------------------------------------------------

            if st.button("بدء التحليل والقياس ✨"):
                with st.spinner("جاري التحليل والقياس بالأرقام..."):
                    
                    # 5. بناء الـ Prompt الجديد والدقيق جداً (The Core Solution)
                    
                    # أمر المعايرة (Calibration Prompt) - ثابت
                    calibration_instruction = f"""
                    You are an expert dental radiologist. First, identify the calibration grid lines present in the image (if any). The vertical distance between adjacent horizontal lines is exactly {MM_PER_LINE_GAP}mm. Perform pixel-to-mm calibration based on this fact.
                    """
                    
                    # أمر التحليل الطبي - ثابت
                    clinical_instruction = """
                    Provide a concise clinical analysis: visible teeth, roots, caries, or lesions.
                    """
                    
                    # أمر القياس (Dynamic Measurement Prompt) - ديناميكي بناءً على طلب الدكتور
                    if user_measurement_request:
                        # لو الدكتور كتب حاجة، نستخدمها هي
                        measurement_instruction = f"""
                        Second, perform the following dynamic measurement as requested: "{user_measurement_request}". Report the final measurement in MM (Millimeters).
                        """
                    else:
                        # لو مكتبش، نعمل قياس افتراضي
                        measurement_prompt = "- Specific Task: Provide full tooth length from occlusal surface to apex."
                        measurement_instruction = f"""
                        Second, if no specific request is provided, provide a general estimate of the full tooth length (Occlusal to Apex) in MM (Millimeters).
                        """
                        
                    # تجميع الأمر النهائي
                    final_prompt = [
                        calibration_instruction,
                        clinical_instruction,
                        measurement_instruction,
                        "\nProvide the output in English, but the response text itself should be easily understandable by an Arabic-speaking dentist.",
                        image
                    ]
                    
                    # إرسال الصورة للموديل
                    response = model.generate_content(final_prompt)
                    
                    st.success("تم التحليل بنجاح!")
                    
                    # عرض التقرير والقياس
                    st.markdown(response.text)

    except Exception as e:
        st.error("❌ حدث خطأ:")
        st.code(str(e))
else:
    st.info("💡 أدخل المفتاح (API Key) في القائمة الجانبية للبدء.")
