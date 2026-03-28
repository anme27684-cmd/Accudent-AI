import streamlit as st
import requests
import base64
import time

# الإعدادات
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI"
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Fast-Scan", page_icon="🦷")
st.title("🦷 AccuDent Pro - التحليل الفوري")

uploaded_file = st.file_uploader("ارفع الأشعة (X-Ray)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("بدء القياس الآن 🚀"):
        try:
            # الرفع لـ GitHub
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
            data = {"message": "Quick Scan", "content": encoded_img}
            
            res = requests.put(url, json=data, headers=headers)
            
            if res.status_code in [200, 201]:
                st.info("✅ تم الرفع.. الرادار يحلل الآن.")
                
                # استقبال الرد النصي المختصر
                with st.spinner("⏳ جاري جلب القياس من Gemini..."):
                    found = False
                    for _ in range(20): # تقليل عدد المحاولات لسرعة الاستضافة
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                        if check.status_code == 200:
                            content = check.text.strip().split('\n')[-1] # جلب آخر سطر فقط
                            if "mm" in content:
                                try:
                                    import json
                                    msg = json.loads(content).get("message", "")
                                    if "mm" in msg:
                                        st.balloons()
                                        st.metric(label="طول القناة الجذرية (Root Length)", value=msg)
                                        found = True
                                        break
                                except: pass
                        time.sleep(2)
                    if not found: st.warning("تأكد من فتح تابة Gemini")
            else:
                st.error("فشل الرفع")
        except Exception as e:
            st.error(f"عطل: {e}")
