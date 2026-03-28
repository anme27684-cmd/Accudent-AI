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
    # هنا بنفترض إنك رفعت الصورة وجبت الـ img_url
    # لو لسه معندكش دالة الرفع، ده لينك تجريبي للاختبار فقط:
    img_url = "رابط_الصورة_المرفوعة_على_جيت_هاب_هنا" 

    # 2. إرسال اللينك للتليجرام (مرة واحدة فقط)
    if "sent_url" not in st.session_state or st.session_state.sent_url != img_url:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": img_url}
            )
            st.session_state.sent_url = img_url
            st.success("🤖 تم إرسال الأشعة للتحليل التلقائي..")
        except:
            st.error("خطأ في الاتصال بالساعي")

# 3. جزء عرض النتيجة
st.markdown("---")
if st.button("جلب التشخيص 🔄"):
    with st.spinner("جاري جلب الرد من Gemini..."):
        try:
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1").json()
            if res.get("ok") and len(res["result"]) > 0:
                msg = res["result"][0]["message"].get("text", "")
                if "تحليل" in msg or "mm" in msg:
                    st.success("✅ النتيجة جاهزة:")
                    st.info(msg)
                    st.balloons()
                else:
                    st.warning("التحليل لسه مخلصش.. استنى ثواني ودوس تاني.")
        except:
            st.error("عطل فني في جلب البيانات.")
