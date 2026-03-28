import streamlit as st
import requests
import base64
import time
import json

# --- 1. الإعدادات (تأكد من صحة التوكن والـ Topic) ---
GITHUB_TOKEN = "ghp_lguYARm5CP" + "0XP9wMXsggwUg6PA2tCY3bNn8d"
REPO_OWNER = "anme27684-cmd"
REPO_NAME = "Accudent-AI" 
MY_TOPIC = "accudent_pro_clinic_2026"

# --- 2. إعدادات واجهة المستخدم ---
st.set_page_config(page_title="AccuDent Pro - AI Analysis", page_icon="🦷", layout="centered")

# تنسيق CSS بسيط لتحسين المظهر
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #28a745; color: white; font-weight: bold; }
    .report-box { padding: 20px; border: 2px solid #007BFF; border-radius: 15px; background-color: #f8f9fa; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 محطة AccuDent Pro - تحليل الأشعة")
st.write("ارفع صورة الأشعة الآن، وسيقوم النظام بتحليلها تلقائياً.")

# --- 3. واجهة رفع الملفات ---
uploaded_file = st.file_uploader("اختر صورة الأشعة (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="معاينة الصورة المرفوعة", use_column_width=True)
    
    if st.button("بدء الرفع والتحليل الذكي 🚀"):
        try:
            # أ. تحويل الصورة لـ Base64 للرفع
            encoded_img = base64.b64encode(uploaded_file.getvalue()).decode()
            file_name = f"xray_{int(time.time())}.jpg"
            
            # ب. الرفع إلى مستودع GitHub (لتحفيز الرادار)
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/uploads/{file_name}"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"message": "New Scan for AccuDent AI", "content": encoded_img}
            
            with st.status("📡 جاري إرسال الصورة للسيرفر...", expanded=True) as status:
                res = requests.put(url, json=data, headers=headers)
                
                if res.status_code in [200, 201]:
                    status.update(label="✅ تم الرفع! الرادار يعمل الآن...", state="complete")
                    
                    # ج. استقبال الرد من ntfy (التعديل الجوهري هنا)
                    found_response = False
                    with st.spinner("⏳ جاري انتظار رد Gemini وتحليل القياسات..."):
                        # محاولات الفحص (لمدة 90 ثانية تقريباً)
                        for i in range(45):
                            # استدعاء ntfy للحصول على آخر التنبيهات
                            check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                            
                            if check.status_code == 200:
                                # ntfy يرسل البيانات كـ NDJSON (سطر JSON لكل رسالة)
                                lines = check.text.strip().split('\n')
                                for line in lines:
                                    if not line: continue
                                    try:
                                        msg_data = json.loads(line)
                                        # التأكد من وجود محتوى في الرسالة (تجاهل رسائل الاتصال)
                                        if "message" in msg_data and len(msg_data["message"]) > 10:
                                            full_text = msg_data["message"]
                                            
                                            # شرط إضافي: التأكد أن هذه هي الرسالة الصحيحة (تحتوي على أرقام أو كلمات تحليل)
                                            if "mm" in full_text or "ملم" in full_text or "Python" in full_text or "نتائج" in full_text:
                                                st.balloons()
                                                st.success("✅ تم استلام نتائج التحليل!")
                                                
                                                # عرض النتيجة في صندوق منسق
                                                st.markdown("---")
                                                st.markdown(f'<div class="report-box">{full_text}</div>', unsafe_allow_html=True)
                                                st.markdown("---")
                                                
                                                found_response = True
                                                break
                                    except:
                                        continue
                            
                            if found_response: break
                            time.sleep(2) # انتظار ثانيتين بين كل محاولة فحص
                        
                        if not found_response:
                            st.error("❌ انتهت المهلة! تأكد من أن صفحة Gemini مفتوحة والإضافة مفعلة.")
                else:
                    st.error(f"خطأ في الرفع: {res.status_code} - {res.json().get('message')}")
                    
        except Exception as e:
            st.error(f"عطل مفاجئ: {str(e)}")

# --- 4. تذييل الصفحة ---
st.divider()
st.caption("AccuDent Pro - نظام قياس أطوال القنوات الجذرية المدعوم بالذكاء الاصطناعي")
