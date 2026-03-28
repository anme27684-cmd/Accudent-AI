import streamlit as st
import requests
import base64
import time

# --- 1. إعدادات النظام (بياناتك يا دكتور) ---
GITHUB_TOKEN = "ghp_u9h4W7R2m8K0zL5pXq9N3vJ6b1Y8d4s2x1A0" # التوكن الخاص بك
REPO_NAME = "Osama-Alaa/accudent-ai" # المستودع الخاص بك
BRANCH = "main"
BOT_TOKEN = "8593652058:AAG_J9d27CLcDVZaTEouSyBG_Iy8D1OAejM"
CHAT_ID = "966563714"

st.set_page_config(page_title="AccuDent AI Pro", page_icon="🦷")
st.title("🦷 AccuDent AI: Automated Diagnostic System")
st.markdown("---")

# --- 2. دالة الرفع لـ GitHub ---
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
            "message": f"New Scan {file_name}",
            "content": content_base64,
            "branch": BRANCH
        }
        
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            # الرابط المباشر (الذي سيقرأه جيمناي)
            return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{file_name}"
        else:
            st.error(f"GitHub Error: {response.json().get('message')}")
            return None
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

# --- 3. واجهة المستخدم ومنطق التشغيل ---
uploaded_file = st.file_uploader("ارفع أشعة المريض هنا (Digital Periapical)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # منع إرسال نفس الملف مرتين
    if "current_img" not in st.session_state or st.session_state.current_img != uploaded_file.name:
        with st.spinner("🚀 جاري الرفع والتحويل لـ AI..."):
            img_url = upload_to_github(uploaded_file)
            
            if img_url:
                # إرسال اللينك للتليجرام لكي تلتقطه الإضافة (Extension)
                tg_res = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": img_url}
                )
                if tg_res.status_code == 200:
                    st.session_state.current_img = uploaded_file.name
                    st.session_state.last_url = img_url
                    st.success("✅ تمت العملية! جيمناي يقوم بالتحليل الآن...")
                else:
                    st.error("فشل التواصل مع التليجرام.")

# --- 4. عرض النتيجة النهائية ---
st.markdown("---")
st.subheader("📊 تقرير التشخيص")

if st.button("تحديث واستلام النتيجة 🔄"):
    with st.spinner("جاري جلب الرد من المحرك..."):
        # جلب آخر رسالة من البوت (التي أرسلتها الإضافة بعد التحليل)
        try:
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1").json()
            if res.get("ok") and len(res["result"]) > 0:
                # البحث عن آخر رسالة تحتوي على "تحليل" أو "mm"
                msg = res["result"][0].get("message", {}).get("text", "")
                if "تحليل" in msg or "mm" in msg or "مم" in msg:
                    st.success("✅ تم استلام التشخيص!")
                    st.write(msg)
                    st.balloons()
                else:
                    st.warning("التحليل قيد المعالجة في تابة Gemini.. انتظر 5 ثوانٍ وجرب مرة أخرى.")
        except:
            st.error("عطل في جلب البيانات.")

st.info("💡 تأكد من فتح تابة Gemini في المتصفح وتفعيل الإضافة لكي يعمل النظام تلقائياً.")
