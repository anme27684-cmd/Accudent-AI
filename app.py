import streamlit as st
import requests
import base64
import time

# --- الإعدادات بالتوكن الجديد ---
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI" 
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - GitHub Station")

uploaded_file = st.file_uploader("ارفع صورة الأشعة (X-Ray)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("تحليل الأشعة الآن 🚀"):
        try:
            # 1. تجهيز الصورة
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            
            # 2. الرفع باستخدام الـ Headers المتوافقة مع Fine-grained Token
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"message": "MVP Scan", "content": encoded_img}
            
            res = requests.put(url, json=data, headers=headers)
            
            if res.status_code in [200, 201]:
                img_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/uploads/{file_name}"
                st.success("✅ تم الرفع بنجاح!")
                st.warning("⚠️ انسخ الرابط ده (Copy) عشان يبدأ التحليل:")
                st.code(img_url)
                
                # 3. استقبال الرد
                with st.spinner("في انتظار رد Gemini..."):
                    found = False
                    for _ in range(45):
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                        if check.status_code == 200:
                            try:
                                msgs = check.json()
                                if msgs:
                                    st.balloons()
                                    st.success("✅ نتيجة القياس:")
                                    st.markdown(f"### {msgs[-1]['message']}")
                                    found = True
                                    break
                            except: pass
                        time.sleep(2)
                    if not found:
                        st.error("المحرك لم يرد بعد، تأكد من تشغيل الكونسول.")
            else:
                st.error(f"خطأ {res.status_code}: {res.json().get('message')}")
        except Exception as e:
            st.error(f"عطل: {e}")
