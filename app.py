import streamlit as st
import requests
import time

# الاسم الثابت بتاعنا
MY_TOPIC = "accudent_pro_clinic_2026" 

st.set_page_config(page_title="AccuDent Pro", page_icon="🦷")
st.title("🦷 AccuDent Pro - MVP")

uploaded_file = st.file_uploader("ارفع الأشعة هنا", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("الرفع وتوليد الرابط 🚀"):
        files = {'file': uploaded_file.getvalue()}
        # استخدام موقع أضمن (catbox.moe) أو الرجوع لـ file.io بفلتر
        res = requests.post('https://file.io', files=files)
        
        if res.status_code == 200:
            img_url = res.json().get('link', '')
            if img_url:
                st.success("✅ الرابط جاهز!")
                st.text_input("انسخ الرابط ده (Ctrl+C):", value=img_url)
                
                with st.spinner("في انتظار تحليل Gemini Pro..."):
                    for _ in range(30):
                        # بنشيك على ntfy
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                        if check.status_code == 200:
                            msgs = check.json()
                            if msgs:
                                st.balloons()
                                st.success("✅ النتيجة النهائية:")
                                st.info(msgs[-1]['message'])
                                break
                        time.sleep(2)
