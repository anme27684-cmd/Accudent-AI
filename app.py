import streamlit as st
import requests
import base64
import time

# --- الإعدادات ---
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI"
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - التحليل الذكي")

uploaded_file = st.file_uploader("ارفع صورة الأشعة (X-Ray)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("تحليل الأشعة الآن 🚀"):
        try:
            # 1. الرفع لـ GitHub
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
            data = {"message": "MVP Scan", "content": encoded_img}
            
            res = requests.put(url, json=data, headers=headers)
            
            if res.status_code in [200, 201]:
                st.success("✅ تم الرفع بنجاح! الرادار يعمل...")
                
                # 2. استقبال الرد (النسخة المختصرة)
                with st.spinner("⏳ في انتظار نتيجة القياس من Gemini..."):
                    found = False
                    # محاولات فحص ntfy (نبحث عن نص عادي)
                    for _ in range(30): 
                        # نطلب النص الخام مباشرة (Plain Text)
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/raw")
                        
                        if check.status_code == 200 and check.text.strip():
                            # نأخذ آخر سطر في الرد
                            last_line = check.text.strip().split('\n')[-1]
                            
                            if "mm" in last_line:
                                st.balloons()
                                st.markdown("### 📊 نتيجة القياس النهائية:")
                                # عرض النتيجة بشكل ضخم وواضح
                                st.metric(label="طول القناة (Root Length)", value=last_line)
                                found = True
                                break
                        time.sleep(2)
                        
                    if not found:
                        st.error("⚠️ لم يتم استلام الرد. تأكد أن تابة Gemini مفتوحة.")
            else:
                st.error(f"خطأ في الرفع: {res.status_code}")
        except Exception as e:
            st.error(f"عطل فني: {e}")
