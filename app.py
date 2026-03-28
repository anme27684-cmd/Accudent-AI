import streamlit as st
import requests, base64, time

GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
FIREBASE_URL = "https://accudent-pro-default-rtdb.firebaseio.com/measurement.json"

st.title("🦷 AccuDent Pro - API Sync")
uploaded_file = st.file_uploader("ارفع الأشعة", type=["jpg", "png", "jpeg"])

if uploaded_file and st.button("تحليل الآن 🚀"):
    # كود الرفع لـ GitHub (نفسه)
    # ...
    
    placeholder = st.empty()
    st.info("⏳ جاري سحب النتيجة من الـ API...")
    
    for _ in range(40):
        try:
            res = requests.get(FIREBASE_URL).json()
            if res and "result" in res:
                # التأكد إن النتيجة جديدة (في آخر 30 ثانية مثلاً)
                if time.time() * 1000 - res['timestamp'] < 30000:
                    st.balloons()
                    st.metric("القياس النهائي", res['result'])
                    st.success("تم الاستلام عبر Google Firebase")
                    st.stop()
        except: pass
        time.sleep(2)
