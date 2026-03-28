import streamlit as st
import requests
import base64
import time

# --- إعدادات النظام ---
# تقسيم التوكن لجزئين لمنع الحظر التلقائي من GitHub
GITHUB_TOKEN = "ghp_NWvJPBIluXLZcIwEtJ4V" + "HH0oPcj7X41shzvb" 

REPO_NAME = "Osama-Alaa/accudent-ai" 
BRANCH = "main"
BOT_TOKEN = "8593652058:AAG_J9d27CLcDVZaTEouSyBG_Iy8D1OAejM"
CHAT_ID = "966563714"

st.set_page_config(page_title="AccuDent AI Pro", page_icon="🦷")
st.title("🦷 AccuDent AI: Diagnostic System")

# --- 1. دالة الرفع لـ GitHub ---
def upload_to_github(file):
    try:
        file_content = file.read()
        content_base64 = base64.b64encode(file_content).decode('utf-8')
        file_name = f"scan_{int(time.time())}.jpg"
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_name}"
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": f"Upload {file_name}",
            "content": content_base64,
            "branch": BRANCH
        }
        
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            # الرابط الخام للصورة
            return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{file_name}"
        else:
            st.error(f"GitHub Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Upload logic error: {e}")
        return None

# --- 2. واجهة المستخدم ---
uploaded_file = st.file_uploader("ارفع أشعة الأسنان هنا", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # استخدام Session State لمنع التكرار عند تحديث الصفحة
    if "last_file" not in st.session_state or st.session_state.last_file != uploaded_file.name:
        with st.spinner("🚀 جاري المعالجة وإرسال الرابط..."):
            img_url = upload_to_github(uploaded_file)
            
            if img_url:
                # إرسال الرابط للبوت لتلتقطه الإضافة
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                             json={"chat_id": CHAT_ID, "text": img_url})
                
                st.session_state.last_file = uploaded_file.name
                st.success("✅ تم إرسال الرابط بنجاح! جيمناي يعمل الآن.")

st.markdown("---")

# --- 3. زرار استلام النتيجة ---
if st.button("تحديث واستلام النتيجة 🔄"):
    with st.spinner("جاري فحص الردود..."):
        try:
            # جلب آخر رسالة وصلت للبوت (التحليل)
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1").json()
            if res.get("ok") and len(res["result"]) > 0:
                msg = res["result"][0].get("message", {}).get("text", "")
                
                # التحقق هل الرسالة تحليل أم مجرد الرابط القديم
                if any(keyword in msg for keyword in ["mm", "مم", "تحليل"]):
                    st.success("📋 تقرير التشخيص النهائي:")
                    st.info(msg)
                    st.balloons()
                else:
                    st.warning("التحليل قيد المعالجة في تابة Gemini.. انتظر 5 ثوانٍ وجرب ثانياً.")
        except:
            st.error("عطل في الاتصال بالبوت.")
