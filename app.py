import streamlit as st
import requests
import base64
import time

GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI"
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro", page_icon="🦷")
st.title("🦷 AccuDent Pro - التحليل المباشر")

uploaded_file = st.file_uploader("ارفع الأشعة", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("تحليل الآن 🚀"):
        try:
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            res = requests.put(url, json={"message": "upload", "content": encoded_img}, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
            
            if res.status_code in [200, 201]:
                st.info("✅ تم الرفع.. بانتظار جيمناي")
                placeholder = st.empty()
                
                # البحث عن النتيجة
                for i in range(40): # محاولات كافية
                    placeholder.text(f"⏳ جاري الفحص... محاولة ({i+1}/40)")
                    # نستخدم poll=1 عشان نستنى رسالة جديدة فعلاً
                    check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1&since=now")
                    if check.status_code == 200:
                        try:
                            # ntfy json بيبعت كذا سطر، بناخد الأخير
                            lines = check.text.strip().split('\n')
                            for line in reversed(lines):
                                msg_data = requests.utils.json.loads(line)
                                msg_text = msg_data.get("message", "")
                                if "mm" in msg_text:
                                    placeholder.empty()
                                    st.balloons()
                                    st.metric("القياس النهائي", msg_text)
                                    st.success("تم استلام القياس بدقة!")
                                    break
                            else: continue
                            break
                        except: pass
                    time.sleep(1.5)
            else: st.error("فشل الرفع")
        except Exception as e: st.error(str(e))
