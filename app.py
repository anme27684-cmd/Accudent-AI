import streamlit as st
import requests
import base64
import time

# --- الإعدادات الثابتة لمشروعك ---
GITHUB_TOKEN = "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"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI" 
MY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - GitHub Station")

uploaded_file = st.file_uploader("ارفع صورة الأشعة (X-Ray)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("بدء الرفع والتحليل التلقائي 🚀"):
        try:
            # 1. تحويل الصورة لكود نصي للرفع
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            
            # 2. الرفع لـ GitHub API (بيعمل فولدر uploads لوحده)
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            data = {"message": "Upload via App", "content": encoded_img}
            
            res = requests.put(url, json=data, headers=headers)
            
            if res.status_code in [200, 201]:
                # رابط الصورة المباشر اللي Gemini هيشوفه
                img_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/uploads/{file_name}"
                st.success("✅ تم الرفع بنجاح!")
                st.warning("⚠️ الخطوة الأخيرة: اضغط كليك يمين واعمل Copy للرابط ده:")
                st.code(img_url)
                
                # 3. الانتظار لسماع الرد من Gemini
                with st.spinner("جاري انتظار تحليل المحرك الذكي..."):
                    found = False
                    for _ in range(40): # هينتظر دقيقة وثلث
                        check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                        if check.status_code == 200 and check.text:
                            msgs = check.json()
                            if msgs:
                                st.balloons()
                                st.success("✅ نتيجة القياس من Gemini:")
                                st.info(msgs[-1]['message'])
                                found = True
                                break
                        time.sleep(2)
                    if not found:
                        st.error("المحرك اتأخر في الرد، تأكد إن تابة Gemini مفتوحة والكونسول شغال.")
            else:
                st.error(f"فشل الرفع. كود الخطأ: {res.status_code}. تأكد من صلاحيات التوكن.")
        except Exception as e:
            st.error(f"عطل فني: {e}")
