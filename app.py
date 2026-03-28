import streamlit as st
import requests
import time

# الاسم الثابت اللي اخترناه
MY_TOPIC = "accudent_dentist_pro_2026" 

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - MVP Station")

uploaded_file = st.file_uploader("ارفع الأشعة هنا", type=["jpg", "png"])

if uploaded_file:
    if st.button("بدء التحليل التلقائي 🚀"):
        # رفع الصورة لموقع مؤقت للحصول على رابط
        files = {'file': uploaded_file.getvalue()}
        res = requests.post('https://file.io', files=files)
        
        if res.status_code == 200:
            img_url = res.json()['link']
            st.warning("1. اضغط كليك يمين واعمل Copy للرابط اللي تحت ده:")
            st.code(img_url)
            
            # الانتظار لسماع الرد من ntfy
            with st.spinner("جاري انتظار رد المحرك (Gemini Pro)..."):
                for _ in range(30): # هيدور لمدة دقيقة تقريباً
                    # بيشيك هل فيه رسالة جديدة وصلت على القناة؟
                    check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                    if check.status_code == 200 and check.text:
                        data = check.json()
                        if data:
                            st.success("✅ النتيجة وصلت:")
                            st.markdown(f"### {data[-1]['message']}")
                            break
                    time.sleep(2)
