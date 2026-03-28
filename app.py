import streamlit as st
import requests, base64, time

GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI"
MY_TOPIC = "accudent_pro_clinic_2026"

st.title("🦷 AccuDent Pro")
uploaded_file = st.file_uploader("ارفع الأشعة", type=["jpg", "png", "jpeg"])

if uploaded_file and st.button("تحليل 🚀"):
    encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
    file_name = f"xray_{int(time.time())}.jpg"
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
    res = requests.put(url, json={"message":"up","content":encoded_img}, headers={"Authorization":f"Bearer {GITHUB_TOKEN}"})
    
    if res.status_code in [200, 201]:
        st.info("⏳ بانتظار جيمناي...")
        for _ in range(30):
            # بنقرأ آخر 5 رسايل ونشوف لو فيهم mm
            check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
            if check.status_code == 200:
                for line in check.text.strip().split('\n'):
                    try:
                        m = requests.utils.json.loads(line).get("message","")
                        if "mm" in m:
                            st.balloons()
                            st.metric("النتيجة", m)
                            st.stop()
                    except: pass
            time.sleep(2)
