import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -- تنسيق CSS كامل لحل كل مشاكل الألوان والنصوص --
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        min-height: 100vh;
        padding-top: 30px;
    }

    /* عنوان الصفحة */
    h1 {
        color: #222222;
        font-size: 55px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
        margin-bottom: 20px;
    }

    /* النصوص العادية */
    label, p, span {
        color: #eeeeee !important;
        font-family: 'Cairo', sans-serif;
        font-size: 16px;
    }

    /* الحقول Input + Selectbox */
    .stTextInput > div > div,
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 10px;
    }

    /* القائمة المفتوحة للدروبوكس */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-weight: 600 !important;
    }

    /* النصوص داخل خيارات الدروبوكس */
    div[data-baseweb="select"] div[role="option"] {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-weight: 600;
    }

    /* العنصر المختار لما تدوس عليه */
    div[data-baseweb="select"] div[aria-selected="true"] {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
    }

    /* زرار البحث */
    button[kind="primary"] {
        background: #0D47A1;
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px 25px;
        border: none;
        transition: 0.3s;
    }

    button[kind="primary"]:hover {
        background: #1565C0;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -- عنوان الصفحة --
st.markdown("<h1>Bravo News 🌍</h1>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# -- مصادر الأخبار الجاهزة --
rss_feeds = {
    "BBC Arabic": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN Arabic": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 Arabic": "https://www.france24.com/ar/rss",
    "Asharq Al-Awsat": "https://aawsat.com/home/rss.xml"
}

# -- عناصر واجهة المستخدم --
selected_feed = st.selectbox("Choose a news source:", list(rss_feeds.keys()))
custom_rss = st.text_input("🛠️ Custom RSS (optional):")
keywords_input = st.text_input("🔎 Search by keywords (optional):")
keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []

# -- دالة جلب الأخبار من رابط RSS --
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
                    "Published": published,
                    "Title": title,
                    "Summary": summary,
                    "Link": link
                })
        else:
            news_list.append({
                "Published": published,
                "Title": title,
                "Summary": summary,
                "Link": link
            })

    return news_list, total_entries

# -- زرار استخراج الأخبار --
if st.button("🔍 Extract News"):
    with st.spinner("⏳ Fetching news..."):
        rss_url = custom_rss if custom_rss else rss_feeds[selected_feed]
        
        news, total_entries = fetch_news_from_rss(rss_url, keywords)
        
        if total_entries == 0:
            st.error("❌ The selected feed has no current news or is invalid.")
        elif news:
            st.success(f"✅ Found {len(news)} matching articles out of {total_entries} available.")
            df = pd.DataFrame(news)
            st.dataframe(df)

            # حفظ الأخبار كملف Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="📥 Download as Excel",
                data=output.getvalue(),
                file_name="bravo_news.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning(f"⚠️ No matching news found, but {total_entries} items exist in the feed.")
