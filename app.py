import streamlit as st
import requests
import time

BOT_TOKEN = "8593652058:AAG_J9d27CLcDVZaTEouSyBG_Iy8D1OAejM"
CHAT_ID = "966563714"

# --- 1. مرحلة إرسال اللينك (بعد ما ترفع الصورة لـ Github) ---
# افترض إنك بترفع الصورة وعندك متغير اسمه img_url فيه اللينك
if uploaded_file is not None:
    # img_url = upload_to_github(uploaded_file) # دي الدالة بتاعتك اللي عملناها قبل كدة
    
    # التأكد إننا بنبعت اللينك ده مرة واحدة بس عشان نمنع الـ Loop
    if "sent_url" not in st.session_state or st.session_state.sent_url != img_url:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": img_url}
            )
            st.session_state.sent_url = img_url
            st.success("🤖 تم إرسال الأشعة للتحليل التلقائي.. يرجى الانتظار بضع ثوانٍ.")
        except Exception as e:
            st.error("حدث خطأ في الإرسال.")

# --- 2. مرحلة جلب النتيجة ---
st.markdown("---")
st.subheader("نتيجة التحليل 🦷")

def get_latest_diagnosis():
    try:
        # بنجيب آخر رسالة وصلت للبوت
        res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1").json()
        if res.get("ok") and len(res["result"]) > 0:
            msg = res["result"][0]["message"].get("text", "")
            # نتأكد إن دي رسالة النتيجة (مش رسالة اللينك اللي لسه باعتينها)
            if "تحليل AccuDent" in msg or "mm" in msg or "مم" in msg:
                return msg
    except:
        pass
    return None

# زرار لتحديث النتيجة بدون عمل Loop في السيرفر
if st.button("جلب التشخيص 🔄"):
    with st.spinner("جاري التواصل مع المحرك..."):
        time.sleep(1) # تأخير بسيط لضمان استقرار السيرفر
        diagnosis = get_latest_diagnosis()
        
        if diagnosis:
            st.success("تم استلام التقرير بنجاح!")
            st.info(diagnosis)
            st.balloons()
        else:
            st.warning("التقرير لم يجهز بعد.. تأكد من أن تابة Gemini مفتوحة، ثم حاول التحديث مرة أخرى.")
