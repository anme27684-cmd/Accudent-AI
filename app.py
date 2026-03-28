import streamlit as st
import requests
import time

# نفس الاسم الثابت بتاعنا
MY_TOPIC = "accudent_dentist_pro_2026" 

st.set_page_config(page_title="AccuDent Pro MVP", page_icon="🦷")
st.title("🦷 AccuDent Pro - MVP Station")

uploaded_file = st.file_uploader("ارفع الأشعة هنا", type=["jpg", "jpeg", "png"])

if uploaded_file:
    if st.button("بدء التحليل التلقائي 🚀"):
        try:
            # محاولة رفع الصورة لموقع tmp.link (أكثر استقراراً)
            files = {'file': uploaded_file.getvalue()}
            # استخدمت موقع file.io تانى بس مع Headers عشان الحماية
            res = requests.post('https://file.io', files=files, headers={'User-Agent': 'Mozilla/5.0'})
            
            if res.status_code == 200:
                data = res.json()
                if 'link' in data:
                    img_url = data['link']
                    st.warning("1. اضغط كليك يمين واعمل Copy للرابط ده:")
                    st.code(img_url)
                    
                    with st.spinner("جاري انتظار رد المحرك (Gemini Pro)..."):
                        for _ in range(30):
                            check = requests.get(f"https://ntfy.sh/{MY_TOPIC}/json?poll=1")
                            if check.status_code == 200:
                                try:
                                    msgs = check.json()
                                    if msgs:
                                        st.success("✅ النتيجة وصلت:")
                                        st.markdown(f"### {msgs[-1]['message']}")
                                        break
                                except:
                                    pass
                            time.sleep(2)
                else:
                    st.error("الموقع مبعتش لينك، جرب ترفع الصورة تاني.")
            else:
                st.error(f"خطأ في السيرفر: {res.status_code}")
                
        except Exception as e:
            st.error(f"حصلت مشكلة تقنية: {e}")
