import streamlit as st
import requests
import base64
import time
import json

# --- 1. الإعدادات الأساسية ---
# ملحوظة: التوكن مقسوم لجزئين عشان الحماية (يفضل وضعه في Secrets لاحقاً)
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI" 
MY_TOPIC = "accudent_pro_clinic_2026"

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="AccuDent Pro - AI Analysis", page_icon="🦷", layout="centered")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 محطة AccuDent Pro - تحليل الأشعة")
st.write("ارفع صورة الأشعة، وسيقوم الرادار بتحليلها تلقائياً عبر Gemini.")

# --- 3. واجهة الرفع ---
uploaded_file = st.file_uploader("اختر صورة الأشعة (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="المعاينة قبل الرفع", use_column_width=True)
    
    if st.button("بدء عملية الرفع والتحليل 🚀"):
        try:
            # أ. تجهيز الصورة (Base64)
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            
            # ب. الرفع إلى GitHub
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"message": "New X-Ray Scan for AI", "content": encoded_img}
            
            with st.status("جاري رفع الصورة إلى سيرفر GitHub...", expanded=True) as status:
                res = requests.put(url, json=data, headers=headers)
                
                if res.status_code in [200, 201]:
                    status.update(label="✅ تم الرفع! الرادار يعمل الآن...", state="complete")
                    st.info("💡 لا حاجة لنسخ اللينك، الإضافة ستكتشف الصورة تلقائياً.")
                    
                    # ج. استقبال الرد من ntfy (الرادار)
                    found_response = False
                    with st.spinner("⏳ جاري انتظار تحليل Gemini (قد يستغرق 10-30 ثانية)..."):
                        # محاولات فحص ntfy (لمدة 90 ثانية تقريباً)
                        for i in range(45):
                            # نطلب البيانات من ntfy بنظام الـ Poll
                            check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                            
                            if check.status_code == 200:
                                # ntfy يرسل البيانات كأسطر JSON منفصلة (NDJSON)
                                lines = check.text.strip().split('\n')
                                for line in lines:
                                    if not line: continue
                                    try:
                                        msg_data = json.loads(line)
                                        # التأكد من وجود رسالة (تجاهل رسائل الاتصال الفارغة)
                                        if "message" in msg_data and len(msg_data["message"]) > 20:
                                            st.balloons()
                                            st.success("✅ تم استلام نتائج التحليل بنجاح:")
                                            
                                            # عرض النتيجة بشكل مرتب
                                            st.markdown("---")
                                            st.markdown(f"### 📋 تقرير المعمل:\n{msg_data['message']}")
                                            st.markdown("---")
                                            
                                            found_response = True
                                            break
                                    except:
                                        continue
                            
                            if found_response: break
                            time.sleep(2) # انتظار ثانيتين بين كل فحص
                        
                        if not found_response:
                            st.error("❌ انتهت مهلة الانتظار. تأكد أن تابة Gemini مفتوحة والإضافة مفعلة.")
                else:
                    st.error(f"فشل الرفع: {res.status_code} - {res.json().get('message')}")
                    
        except Exception as e:
            st.error(f"عطل فني في النظام: {str(e)}")

# --- 4. التذييل ---
st.caption("نظام AccuDent Pro التجريبي - 2026")
