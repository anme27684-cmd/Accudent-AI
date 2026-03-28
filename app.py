import streamlit as st
import requests
import base64
import time

# --- الإعدادات النهائية (التوكن الكلاسيكي) ---
GITHUB_TOKEN = "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"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI" 
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - Professional Station")

uploaded_file = st.file_uploader("ارفع صورة الأشعة (X-Ray)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("تحليل الأشعة الآن 🚀"):
        try:
            # 1. تجهيز الصورة
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            
            # 2. الرفع باستخدام Classic Token Headers
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"message": "MVP Scan", "content": encoded_img}
            
            res = requests.put(url, json=data, headers=headers)
            
            if res.status_code in [200, 201]:
                img_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/uploads/{file_name}"
                st.success("✅ تم الرفع للخزنة بنجاح!")
                st.warning("⚠️ انسخ الرابط ده (Copy) عشان يبدأ التحليل:")
                st.code(img_url)
                
                # 3. استقبال الرد من ntfy
                with st.spinner("في انتظار رد المحرك الذكي..."):
                    found = False
                    for _ in range(45):
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                        if check.status_code == 200 and check.text:
                            msgs = check.json()
                            if msgs:
                                st.balloons()
                                st.success("✅ تم القياس بنجاح:")
                                st.markdown(f"### {msgs[-1]['message']}")
                                found = True
                                break
                        time.sleep(2)
                    if not found:
                        st.error("تأكد أن تابة Gemini مفتوحة والكونسول شغال.")
            else:
                st.error(f"خطأ {res.status_code}: {res.json().get('message')}")
        except Exception as e:
            st.error(f"عطل: {e}")
