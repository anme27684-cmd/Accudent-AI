import streamlit as st
import requests
import time

# بيانات التليجرام
BOT_TOKEN = "8593652058:AAG_J9d27CLcDVZaTEouSyBG_Iy8D1OAejM"
CHAT_ID = "966563714"

st.title("AccuDent Pro - AI Analysis 🦷")

# 1. زرار رفع الصورة
uploaded_file = st.file_uploader("ارفع صورة الأشعة هنا", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 🔥 هنا لازم نستخدم الدالة اللي بترفع لـ GitHub وترجع لينك حقيقي
    # تأكد إن عندك دالة اسمها upload_to_github في الكود
    img_url = upload_to_github(uploaded_file) 

    # 2. إرسال اللينك الحقيقي للتليجرام
    if img_url and ("sent_url" not in st.session_state or st.session_state.sent_url != img_url):
        try:
            # هنا بنبعت الـ img_url اللي هو اللينك الحقيقي
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": img_url}
            )
            st.session_state.sent_url = img_url
            st.success("🤖 تم إرسال الأشعة للتحليل التلقائي..")
        except:
            st.error("خطأ في الاتصال بالساعي")

# 3. زرار جلب النتيجة (نفس الكود اللي فات)
st.markdown("---")
if st.button("جلب التشخيص 🔄"):
    with st.spinner("جاري جلب الرد..."):
        # كود الـ getUpdates بتاعك هنا
        pass
