import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates
import io

# 1. إعداد الصفحة
st.set_page_config(page_title="Accudent AI - Precision Measurement", page_icon="🦷", layout="centered")

st.title("🦷 Accudent AI: Precision Manual Measurement Tool")
st.write("ارفع صورة الأشعة (X-ray) وقم بتحديد نقاط القياس بدقة.")

# ثابت المعايرة (يمكن تغييره من قبل المستخدم)
MM_PER_LINE_GAP = 1.8

# دالة لتحويل صورة PIL لصورة OpenCV
def pil_to_cv2(pil_image):
    open_cv_image = np.array(pil_image)
    # تحويل من RGB لـ BGR (ما عدا الصور الرمادية)
    if len(open_cv_image.shape) == 3:
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    return open_cv_image

# 2. رفع الصورة
uploaded_file = st.file_uploader("ارفع صورة الأشعة (JPG, PNG)...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # تحميل وعرض الصورة
    img = Image.open(uploaded_file).convert("RGB")
    width, height = img.size
    
    # 3. واجهة المستخدم لاختيار النقاط
    st.markdown("---")
    st.subheader("📍 حدد نقاط القياس بنفسك")
    st.info("💡 انقر على الصورة لتحديد النقاط بالترتيب:")
    st.write("**1.** نقطة على خط المعايرة الأول. | **2.** نقطة على خط المعايرة الثاني (1.8 ملم). | **3.** نقطة البداية (K-file Stopper). | **4.** نقطة النهاية (Root Apex).")

    # تهيئة قائمة النقاط في جلسة المستخدم (session_state)
    if 'coords' not in st.session_state:
        st.session_state.coords = []

    # استخدام مكتبة لتسجيل إحداثيات النقاط عند النقر
    value = streamlit_image_coordinates(img, key="coords_capture")

    # إضافة الإحداثيات المكتشفة للقائمة
    if value:
        point = (value["x"], value["y"])
        # التأكد من عدم إضافة نفس النقطة مرتين متتاليتين
        if not st.session_state.coords or point != st.session_state.coords[-1]:
            st.session_state.coords.append(point)
            # التأكد من عدم تجاوز 4 نقاط
            if len(st.session_state.coords) > 4:
                st.session_state.coords = st.session_state.coords[-4:]

    # عرض النقاط المحددة
    if st.session_state.coords:
        st.write("**النقاط المحددة حالياً:**")
        points_labels = ["خط المعايرة 1", "خط المعايرة 2", "البداية (Stopper)", "النهاية (Apex)"]
        for i, pt in enumerate(st.session_state.coords):
            st.write(f"- {points_labels[i]}: {pt}")

    # زر لإعادة تعيين النقاط
    if st.button("إعادة تعيين النقاط 🔄"):
        st.session_state.coords = []
        st.experimental_rerun()

    # 4. الحساب والرسم عند توفر 4 نقاط
    if len(st.session_state.coords) == 4:
        st.markdown("---")
        if st.button("بدء القياس ورسم الخطوط ✨"):
            with st.spinner("جاري حساب القياس ورسم الخطوط..."):
                
                # الحصول على الإحداثيات
                c1 = np.array(st.session_state.coords[0])
                c2 = np.array(st.session_state.coords[1])
                start = np.array(st.session_state.coords[2])
                end = np.array(st.session_state.coords[3])
                
                # المعايرة (Calibration)
                pixels_between_lines = np.linalg.norm(c1 - c2)
                if pixels_between_lines == 0:
                    st.error("❌ نقاط المعايرة لا يمكن أن تكون متطابقة.")
                    st.stop()
                pixels_per_mm = pixels_between_lines / MM_PER_LINE_GAP
                
                # حساب القياس النهائي
                pixels_file_length = np.linalg.norm(start - end)
                final_length_mm = pixels_file_length / pixels_per_mm
                
                # --- رسم النقاط والخطوط على الصورة ---
                draw_img = img.copy()
                draw = ImageDraw.Draw(draw_img)
                
                # رسم نقاط المعايرة (أخضر)
                draw.ellipse([c1[0]-5, c1[1]-5, c1[0]+5, c1[1]+5], fill="green", outline="white")
                draw.ellipse([c2[0]-5, c2[1]-5, c2[0]+5, c2[1]+5], fill="green", outline="white")
                draw.line([tuple(c1), tuple(c2)], fill="green", width=2)
                
                # رسم خط القياس (أصفر) ونقط البداية والنهاية
                draw.line([tuple(start), tuple(end)], fill="yellow", width=3)
                draw.ellipse([start[0]-8, start[1]-8, start[0]+8, start[1]+8], fill="red", outline="white") # Stopper
                draw.ellipse([end[0]-8, end[1]-8, end[0]+8, end[1]+8], fill="blue", outline="white") # Apex
                
                # عرض الصورة النهائية والنتيجة
                st.subheader("✅ نتيجة القياس الدقيق:")
                st.image(draw_img, caption=f"المعايرة: {pixels_per_mm:.2f} px/mm | القياس: {final_length_mm:.1f} mm", use_container_width=True)
                st.success(f"📏 طول القناة المقاس: **{final_length_mm:.1f} mm**")
                
                # تفاصيل النقط
                st.write("📊 **تفاصيل القياس:**")
                st.write(f"- نقطة البداية (🔴): {tuple(start)}")
                st.write(f"- نقطة النهاية (🔵): {tuple(end)}")
                st.write(f"- نقاط المعايرة (🟢): {tuple(c1)}, {tuple(c2)}")
