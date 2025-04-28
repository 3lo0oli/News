import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -- تنسيق الألوان والخلفية الجديدة --
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        min-height: 100vh;
        padding-top: 30px;
    }
    h1 {
        color: #FFFFFF;
        font-size: 55px;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 10px;
    }
    label, p, div, span {
        color: #e0e0e0 !important;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput > div > div, .stSelectbox > div {
        background-color: #1F1F1F;
        border-radius: 12px;
        border: 1px solid #3A3A3A;
        padding: 10px;
        color: white;
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #00BFFF, #1E90FF);
        color: white;
        font-size: 20px;
        border-radius: 12px;
        padding: 12px 30px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(90deg, #1E90FF, #00BFFF);
        color: white;
    }
    hr {
        margin: 2rem 0;
        border: 0;
        border-top: 1px solid #3A3A3A;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -- العنوان الجديد مع الكورة الأرضية 🌍 بعد النص بدون الإيد 👌 --
st.markdown("<h1>Bravo News 🌍</h1>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# -- المصادر الجاهزة --
rss_feeds = {
    "BBC عربي": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN بالعربية": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 عربي": "https://www.france24.com/ar/rss",
    "الشرق الأوسط": "https://aawsat.com/home/rss.xml"
}

# -- واجهة المستخدم --
selected_feed = st.selectbox("اختر مصدر الأخبار:", list(rss_feeds.keys()))
custom_rss = st.text_input("🛠️ مخصص لتغذية الأخبار (اختياري):")
keywords_input = st.text_input("🔎 بحث بالكلمات المفتاحية (اختياري):")
keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []

# -- دالة استخراج الأخبار --
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

# -- زر استخراج الأخبار --
if st.button("🔍 استخراج الأخبار"):
    with st.spinner("⏳ جاري استخراج الأخبار..."):
        rss_url = custom_rss if custom_rss else rss_feeds[selected_feed]
        
        news, total_entries = fetch_news_from_rss(rss_url, keywords)
        
        if total_entries == 0:
            st.error("❌ المصدر المحدد لا يحتوي على أخبار حالياً أو الرابط غير صالح.")
        elif news:
            st.success(f"✅ تم العثور على {len(news)} خبر يطابق البحث من أصل {total_entries} خبر متاح.")
            df = pd.DataFrame(news)
            st.dataframe(df)

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
