import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -------- إعداد ديزاين CSS مخصص --------
st.markdown("""
    <style>
    /* تغيير لون خلفية الصفحة */
    .stApp {
        background-color: #0D1B2A;
        background-image: url('https://images.unsplash.com/photo-1603052879461-5085c3eb07d4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1400&q=80');
        background-size: cover;
        background-position: center;
    }

    /* تنسيق العنوان */
    h1 {
        color: #ffffff;
        text-align: center;
        font-size: 60px;
        margin-bottom: 50px;
    }

    /* تنسيق النصوص */
    label, p, div, span {
        color: #d1d5db !important;
    }

    /* تخصيص الـ selectbox و الـ input */
    .stTextInput > div > div, .stSelectbox > div {
        background-color: #1B263B;
        border-radius: 10px;
        color: white;
        border: 1px solid #415A77;
        padding: 8px;
    }

    /* تخصيص الزرار */
    button[kind="primary"] {
        background-color: #415A77;
        color: white;
        font-size: 18px;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
    }

    /* تعديل زر التحميل */
    .stDownloadButton > button {
        background-color: #778DA9;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -------- Streamlit App --------
st.markdown("<h1>Bravo News 👌</h1>", unsafe_allow_html=True)

# قائمة التصنيفات الجاهزة
rss_feeds = {
    "BBC عربي": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN بالعربية": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 عربي": "https://www.france24.com/ar/rss",
    "الشرق الأوسط": "https://aawsat.com/home/rss.xml"
}

# اختيار التصنيف
selected_feed = st.selectbox("اختر مصدر الأخبار:", list(rss_feeds.keys()))

# أو أدخل رابط RSS مخصص
custom_rss = st.text_input("🛠️ مخصص لتغذية الأخبار (اختياري):")

# إدخال الكلمات المفتاحية
keywords_input = st.text_input("🔎 بحث الكلمات المفتاحية (اختياري):")
keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []

# -------- استخراج الأخبار من RSS --------
def fetch_news_from_rss(rss_url, keywords):
    feed = feedparser.parse(rss_url)
    news_list = []
    total_entries = len(feed.entries)

    for entry in feed.entries:
        title = entry.title
        summary = entry.get("summary", "")
        link = entry.link
        published = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if keywords:
            if any(keyword.lower() in (title + " " + summary).lower() for keyword in keywords):
                news_list.append({
                    "تاريخ النشر": published,
                    "العنوان": title,
                    "الوصف": summary,
                    "الرابط": link
                })
        else:
            news_list.append({
                "تاريخ النشر": published,
                "العنوان": title,
                "الوصف": summary,
                "الرابط": link
            })

    return news_list, total_entries

# زرار البحث
if st.button("🔍 استخراج الأخبار"):
    with st.spinner("جاري استخراج الأخبار..."):
        rss_url = custom_rss if custom_rss else rss_feeds[selected_feed]
        
        news, total_entries = fetch_news_from_rss(rss_url, keywords)
        
        if total_entries == 0:
            st.error("❌ المصدر المحدد لا يحتوي على أخبار حالياً أو غير صالح.")
        elif news:
            st.success(f"✅ تم العثور على {len(news)} خبر يطابق الكلمات المفتاحية من أصل {total_entries} خبر متاح.")
            df = pd.DataFrame(news)
            st.dataframe(df)

            # حفظ الملف
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="📥 تحميل الأخبار كملف Excel",
                data=output.getvalue(),
                file_name="آخر_الأخبار.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning(f"⚠️ لم يتم العثور على أخبار تطابق الكلمات، لكن المصدر يحتوي على {total_entries} خبر.")

