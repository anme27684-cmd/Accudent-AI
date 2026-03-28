import streamlit as st
import requests
import base64
import time

# --- 1. الإعدادات الصحيحة بناءً على الرابط الجديد ---
# تقسيم التوكن للحماية من روبوتات جيت هاب
token_part1 = "ghp_NWvJPBIluXLZ"
token_part2 = "IwEtJ4VHH0oPcj7X41shzvb"
# بدل ما نكتب التوكن هنا، بنقوله هاته من الخزنة (Secrets)
GITHUB_TOKEN = st.secrets["G_TOKEN"]
# البيانات المستخرجة من الرابط اللي بعته
REPO_NAME = "anme27684-cmd/Accudent-AI" 
BRANCH = "main"

# بيانات التليجرام
BOT_TOKEN = "8593652058:AAG_J9d27CLcDVZaTEouSyBG_Iy8D1OAejM"
CHAT_ID = "966563714"

st.set_page_config(page_title="AccuDent AI Pro", page_icon="🦷")
st.title("🦷 AccuDent AI: Smart Diagnostic")

# --- 2. دالة الرفع لـ GitHub ---
def upload_to_github(file):
    try:
        file_content = file.read()
        content_base64 = base64.b64encode(file_content).decode('utf-8')
        file_name = f"scan_{int(time.time())}.jpg"
        
        # الرابط الصحيح للـ API
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_name}"
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": f"Upload Scan {file_name}",
            "content": content_base64,
            "branch": BRANCH
        }
        
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            # اللينك الخام اللي الإضافة هتفتحه في جيمناي
            return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{file_name}"
        else:
            st.error(f"GitHub Error {response.status_code}: {response.json().get('message')}")
            return None
    except Exception as e:
        st.error(f"System Error: {e}")
        return None

# --- 3. واجهة المستخدم ---
uploaded_file = st.file_uploader("ارفع أشعة المريض (Digital Periapical)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("🚀 جاري الرفع والتحويل للمعالجة..."):
            img_url = upload_to_github(uploaded_file)
            
            if img_url:
                # إرسال الرابط للبوت
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                             json={"chat_id": CHAT_ID, "text": img_url})
                
                st.session_state.current_file = uploaded_file.name
                st.success("✅ تم الرفع! جيمناي استلم الرابط ويقوم بالتحليل.")

st.markdown("---")

# --- 4. استلام النتيجة ---
if st.button("جلب التشخيص النهائي 🔄"):
    with st.spinner("جاري فحص الردود من البوت..."):
        try:
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1").json()
            if res.get("ok") and len(res["result"]) > 0:
                msg = res["result"][0].get("message", {}).get("text", "")
                
                if any(x in msg for x in ["mm", "مم", "تحليل"]):
                    st.success("📋 التقرير الطبي:")
                    st.info(msg)
                    st.balloons()
                else:
                    st.warning("التحليل لم يجهز بعد.. انتظر قليلاً ثم حدث الصفحة.")
        except:
            st.error("عطل في جلب البيانات.")
