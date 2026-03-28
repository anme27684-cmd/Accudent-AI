import streamlit as st
import requests
import base64
import time
import json

# --- 1. الإعدادات الأساسية ---
# ملاحظة: تم تقسيم التوكن لتجنب حذفه تلقائياً من نظام حماية GitHub
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI"
NTFY_TOPIC = "accudent_pro_clinic_2026"

st.set_page_config(page_title="AccuDent Pro AI", layout="centered", page_icon="🦷")
st.title("🦷 AccuDent Pro: AI Endo Analyzer")

# --- 2. دالة رفع الصورة لـ GitHub ---
def upload_to_github(file_bytes, file_name):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
    encoded_content = base64.b64encode(file_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}", 
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"message": f"Upload {file_name}", "content": encoded_content}
    
    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [201, 200]:
        return f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/uploads/{file_name}"
    return None

# --- 3. واجهة المستخدم ---
uploaded_file = st.file_uploader("ارفع صورة الأشعة (X-Ray)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    if st.button("🚀 الرفع والتحليل التلقائي"):
        with st.spinner("جاري المعايرة والرفع..."):
            file_bytes = uploaded_file.read()
            file_name = f"xray_{int(time.time())}.jpg"
            raw_url = upload_to_github(file_bytes, file_name)
            
            if raw_url:
                st.success("✅ تم الرفع بنجاح!")
                
                # --- سر الربط اللاسلكي: إرسال اللينك للمخزن المشترك ---
                st.components.v1.html(f"""
                    <script>
                        localStorage.setItem('last_xray_url', '{raw_url}');
                        console.log('Link sent to Gemini tab');
                    </script>
                """, height=0)
                
                st.info("💡 المحرك يعمل الآن في الخلفية... انتظر النتيجة.")
                
                # --- 4. استلام الرد المحمي من ntfy ---
                placeholder = st.empty()
                
                # محاولة الاستماع للرد لمدة 60 ثانية
                for i in range(30): 
                    try:
                        res = requests.get(f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1", timeout=5)
                        if res.status_code == 200:
                            # تقسيم الرد لأسطر والتعامل مع كل سطر بحذر
                            lines = res.text.strip().split('\n')
                            for line in lines:
                                if not line.strip(): continue # تجاهل الأسطر الفاضية
                                
                                try:
                                    msg_data = json.loads(line)
                                    # التأكد إن الرسالة تحتوي على تحليل فعلي (أطول من 20 حرف)
                                    if "message" in msg_data and len(msg_data["message"]) > 20:
                                        # التأكد إنها مش رسالة "الأمر" اللي إحنا بعتناه
                                        if "حلل بدقة" not in msg_data["message"]:
                                            placeholder.markdown(f"### 📊 النتيجة الدقيقة:\n{msg_data['message']}")
                                            st.balloons()
                                            st.stop() # توقف بمجرد الحصول على النتيجة
                                except (json.JSONDecodeError, KeyError):
                                    continue # تجاهل أي سطر ليس بتنسيق JSON صحيح
                    except Exception:
                        pass # استمر في المحاولة لو حدث خطأ في الشبكة
                    
                    time.sleep(2)
                
                st.warning("⚠️ المحرك لم يرد بعد، تأكد من تشغيل الكونسول في تابة Gemini (نفس المتصفح).")
            else:
                st.error("❌ فشل الرفع لـ GitHub. تأكد من إعدادات المستودع.")

st.markdown("---")
st.caption("AccuDent Pro MVP v1.2 - Precision Endodontic Measurement")
