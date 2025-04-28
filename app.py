import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -- CSS للتنسيق زي الصورة اللي بعتهالي --
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #5C258D, #4389A2);
        min-height: 100vh;
        padding-top: 30px;
    }
    h1 {
        color: #FFFFFF;
        font-size: 50px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
        margin-bottom: 20px;
    }
    label, p, div, span {
        color: #EEEEEE !important;
        font-family: 'Cairo', sans-serif;
        font-size: 16px;
    }
    .stTextInput > div > div, .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        padding: 10px;
        color: #FFFFFF !important;
        border: none;
    }
    .stTextInput > div > div:hover, .stSelectbox > div > div:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
    }
    button[kind="primary"] {
        background-color: #0D47A1;
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px 25px;
        border: none;
        transition: 0.3s;
    }
    button[kind="primary"]:hover {
        background-color: #1565C0;
        color: white;
    }
    hr {
        margin: 2rem 0;
        border: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -- العنوان زي اللي في الصورة --
st.markdown("<h1>برافو الإخباري 👍</h1>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# -- قائمة الأخبار --
rss_feeds = {
    "BBC عربي": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN بالعربية": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 عربي": "https://www.france24.com/ar/rss",
    "الشرق الأوسط": "https://aawsat.com/home/rss.xml"
}

# -- إدخالات المستخدم --
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

# -- زرار استخراج الأخبار --
if st.button("🔍 استخرج الأخبار"):
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
