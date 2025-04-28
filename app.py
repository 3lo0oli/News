import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -- CSS معدلة صح ومجربة --
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        min-height: 100vh;
        padding-top: 30px;
    }

    h1 {
        color: #222;
        text-align: center;
        font-size: 50px;
        font-family: 'Cairo', sans-serif;
        margin-bottom: 20px;
    }

    label, p, span {
        color: #eeeeee !important;
        font-family: 'Cairo', sans-serif;
        font-size: 16px;
    }

    /* نعدل فقط مكان عرض الاختيار مش القايمة */
    .stSelectbox > div:first-child {
        background-color: #fff !important;
        color: #222 !important;
        border-radius: 12px;
        padding: 10px;
        font-weight: 600;
    }

    .stTextInput > div > div {
        background-color: #fff !important;
        color: #111 !important;
        border-radius: 12px;
        padding: 10px;
        font-weight: 600;
    }

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
""", unsafe_allow_html=True)

# -- العنوان Bravo News 🌍 --
st.markdown("<h1>Bravo News 🌍</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# -- مصادر الأخبار --
rss_feeds = {
    "BBC Arabic": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN Arabic": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 Arabic": "https://www.france24.com/ar/rss",
    "Asharq Al-Awsat": "https://aawsat.com/home/rss.xml"
}

# -- واجهة المستخدم --
selected_feed = st.selectbox("Choose a news source:", list(rss_feeds.keys()))
custom_rss = st.text_input("🛠️ Custom RSS (optional):")
keywords_input = st.text_input("🔎 Search by keywords (optional):")
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
