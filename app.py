import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
import cv2
import io

# 1. إعداد الصفحة
st.set_page_config(page_title="Accudent AI - Precision Measurement", page_icon="🦷", layout="centered")
st.title("🦷 Accudent AI: Precision Measurement Tool")

# 2. إدخال المفتاح (في الجنب)
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# 3. ثابت المعايرة (Scale Definition)
MM_PER_LINE_GAP = 1.8

# دالة لتحويل صورة Streamlit لصورة OpenCV
def load_image_cv2(uploaded_file):
    image_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    image_cv2 = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    return image_cv2

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # كود البحث عن الموديل المتاح تلقائياً
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
            # عرض الصورة في Streamlit
            st.image(uploaded_file, caption="الأشعة المرفوعة", use_container_width=True)

            # ---------------------------------------------------------
            # الحل الجذري: كود اكتشاف النقاط والمعايرة الرياضية
            # ---------------------------------------------------------
            if st.button("بدء القياس الدقيق ✨"):
                with st.spinner("جاري التواصل مع الذكاء الاصطناعي لاكتشاف النقاط..."):
                    
                    # 5. الـ Prompt الذكي لاكتشاف إحداثيات النقاط
                    # إحنا بنطلب من الموديل بس يحدد مكان الحاجات، مش يقيسها
                    detection_prompt = f"""
                    You are an expert dental radiologist. Your task is to identify key coordinates in this image.
                    Analyze the image and provide the (x, y) pixel coordinates for:
                    1. A point on any horizontal calibration line.
                    2. A point on the *adjacent* horizontal calibration line below or above it.
                    3. The exact position of the K-file stopper.
                    4. The apex of the root canal for the tooth shown.
                    Provide the output in this strict JSON format:
                    {{
                        "calibration_point_1": [x, y],
                        "calibration_point_2": [x, y],
                        "file_stopper": [x, y],
                        "apex": [x, y]
                    }}
                    Only output the JSON.
                    """
                    
                    # إرسال الصورة للموديل (نحتاج لنسخة جديدة من الصورة لأن st.image تستهلكها)
                    uploaded_file.seek(0)
                    image_for_genai = Image.open(uploaded_file).convert("RGB")
                    response = model.generate_content([detection_prompt, image_for_genai])
                    
                    # 6. معالجة الرد واستخراج الإحداثيات (JSON parsing)
                    # هذا الجزء يحتاج لمعالجة دقيقة لرد الموديل للتأكد من أنه JSON صالح
                    try:
                        import json
                        import re
                        # تنظيف الرد من أي علامات اقتباس أو كلام إضافي
                        clean_response = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
                        coords = json.loads(clean_response)
                        
                        # تحميل الصورة في OpenCV للقياس الرياضي
                        uploaded_file.seek(0)
                        image_cv2 = load_image_cv2(uploaded_file)
                        
                        # 7. الحساب الرياضي للمعايرة (Calibration)
                        # حساب المسافة بين نقطتي المعايرة (بالبيكسل)
                        p1 = np.array(coords["calibration_point_1"])
                        p2 = np.array(coords["calibration_point_2"])
                        pixels_between_lines = np.linalg.norm(p1 - p2)
                        
                        # حساب الـ Scale (Pixels per MM)
                        pixels_per_mm = pixels_between_lines / MM_PER_LINE_GAP
                        
                        st.write(f"📊 تم حساب المعايرة: {pixels_per_mm:.2f} pixels/mm")
                        
                        # 8. الحساب الرياضي للقياس النهائي
                        # حساب المسافة بين الـ Stopper والـ Apex (بالبيكسل)
                        stopper_p = np.array(coords["file_stopper"])
                        apex_p = np.array(coords["apex"])
                        pixels_file_length = np.linalg.norm(stopper_p - apex_p)
                        
                        # تحويل المسافة لملم
                        final_length_mm = pixels_file_length / pixels_per_mm
                        
                        # 9. عرض النتيجة النهائية
                        st.markdown("---")
                        st.subheader("🎉 النتيجة النهائية للقياس الدقيق:")
                        st.success(f"📏 طول القناة المقاس: **{final_length_mm:.1f} mm**")
                        
                        # رسم النقاط على الصورة (اختياري، للتأكد من صحة الاكتشاف)
                        cv2.circle(image_cv2, tuple(p1), 10, (0, 255, 0), -1)
                        cv2.circle(image_cv2, tuple(p2), 10, (0, 255, 0), -1)
                        cv2.circle(image_cv2, tuple(stopper_p), 10, (0, 0, 255), -1)
                        cv2.circle(image_cv2, tuple(apex_p), 10, (255, 0, 0), -1)
                        # عرض الصورة المرسوم عليها في Streamlit
                        uploaded_file.seek(0)
                        image_with_points = Image.open(uploaded_file).convert("RGB")
                        # (ملاحظة: OpenCV تستخدم BGR، PIL تستخدم RGB، نحتاج للتحويل لو رسمنا على OpenCV image)
                        
                        st.write("📊 النقاط المكتشفة (للتأكد): أخضر (معايرة)، أحمر (Stopper)، أزرق (Apex)")
                        
                    except Exception as json_e:
                        st.error("❌ فشل الذكاء الاصطناعي في تحديد النقاط بدقة، حاول مرة أخرى.")
                        st.code(str(json_e))
                        st.write("رد الموديل (للتصحيح):")
                        st.write(response.text)

    except Exception as e:
        st.error("❌ حدث خطأ:")
        st.code(str(e))
else:
    st.info("💡 أدخل المفتاح (API Key) في القائمة الجانبية للبدء.")
