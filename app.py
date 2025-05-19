import streamlit as st
import requests
import feedparser
import pandas as pd
from datetime import datetime
from io import BytesIO
from textblob import TextBlob
from collections import Counter
from docx import Document
from bs4 import BeautifulSoup

st.set_page_config(page_title="📰 أداة الأخبار العربية الذكية", layout="wide")
st.title("🗞️ أداة إدارة وتحليل الأخبار (RSS + Web Scraping)")

category_keywords = {
    "سياسة": ["\u0631\u0626\u064a\u0633", "\u0648\u0632\u064a\u0631", "\u0627\u0646\u062a\u062e\u0627\u0628\u0627\u062a", "\u0628\u0631\u0644\u0645\u0627\u0646", "\u0633\u064a\u0627\u0633\u0629"],
    "رياضة": ["\u0643\u0631\u0629", "\u0644\u0627\u0639\u0628", "\u0645\u0628\u0627\u0631\u0627\u0629", "\u062f\u0648\u0631\u064a", "\u0647\u062f\u0641"],
    "اقتصاد": ["\u0633\u0648\u0642", "\u0627\u0642\u062a\u0635\u0627\u062f", "\u0627\u0633\u062a\u062b\u0645\u0627\u0631", "\u0628\u0646\u0643", "\u0645\u0627\u0644"],
    "تكنولوجيا": ["\u062a\u0642\u0646\u064a\u0629", "\u062a\u0637\u0628\u064a\u0642", "\u0647\u0627\u062a\u0641", "\u0630\u0643\u0627\u0621", "\u0628\u0631\u0645\u062c\u0629"]
}

def summarize(text, max_words=25):
    return " ".join(text.split()[:max_words]) + "..."

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "😃 إيجابي"
    elif polarity < -0.1:
        return "😠 سلبي"
    else:
        return "😐 محايد"

def detect_category(text):
    for category, words in category_keywords.items():
        if any(word in text for word in words):
            return category
    return "غير مصنّف"

def fetch_scraped_news(url, source_name, keywords, date_from, date_to, chosen_category, selector, link_prefix=""):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    news_list = []

    for a in soup.select(selector):
        title = a.text.strip()
        link = a.get("href", "")
        if link_prefix and not link.startswith("http"):
            link = link_prefix + link
        published_dt = datetime.today()

        if keywords and not any(k.lower() in title.lower() for k in keywords):
            continue

        auto_category = detect_category(title)
        if chosen_category != "الكل" and auto_category != chosen_category:
            continue

        news_list.append({
            "source": source_name,
            "title": title,
            "summary": title,
            "link": link,
            "published": published_dt,
            "image": "",
            "sentiment": analyze_sentiment(title),
            "category": auto_category
        })

    return news_list

def fetch_news(source_name, source_data, keywords, date_from, date_to, chosen_category):
    if source_data["type"] == "rss":
        feed = feedparser.parse(source_data["url"])
        news_list = []
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            link = entry.link
            published = entry.get("published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:
                published_dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                published_dt = datetime.now()
            image = ""
            if 'media_content' in entry:
                image = entry.media_content[0].get('url', '')
            elif 'media_thumbnail' in entry:
                image = entry.media_thumbnail[0].get('url', '')

            if not (date_from <= published_dt.date() <= date_to):
                continue

            full_text = title + " " + summary
            if keywords and not any(k.lower() in full_text.lower() for k in keywords):
                continue

            auto_category = detect_category(full_text)
            if chosen_category != "الكل" and auto_category != chosen_category:
                continue

            news_list.append({
                "source": source_name,
                "title": title,
                "summary": summary,
                "link": link,
                "published": published_dt,
                "image": image,
                "sentiment": analyze_sentiment(summary),
                "category": auto_category
            })
        return news_list

    elif source_data["type"] == "scrape":
        return fetch_scraped_news(source_data["url"], source_name, keywords, date_from, date_to, chosen_category, source_data["selector"], source_data.get("prefix", ""))

# المصادر
rss_feeds = {
    "RT Arabic": {"type": "rss", "url": "https://arabic.rt.com/rss/"},
    "Hatha Alyoum": {"type": "scrape", "url": "https://hathalyoum.net/", "selector": ".newstitle a"},
    "Iraq Today": {"type": "scrape", "url": "https://iraqtoday.com/", "selector": ".block-title a"},
    "وزارة الداخلية": {"type": "scrape", "url": "https://moi.gov.iq/", "selector": ".more-news .title-news a", "prefix": "https://moi.gov.iq"},
    "رئاسة الجمهورية": {"type": "scrape", "url": "https://presidency.iq/", "selector": ".article-title a"},
    "الشرق - العراق": {"type": "scrape", "url": "https://asharq.com/tags/العراق/", "selector": "a.Card", "prefix": "https://asharq.com"},
    "RT - العراق": {"type": "scrape", "url": "https://arabic.rt.com/focuses/10744-العراق/", "selector": ".focus-page__item a.focus-page__link", "prefix": "https://arabic.rt.com"},
    "العربية - العراق": {"type": "scrape", "url": "https://x.com/AlArabiya_Iraq?t=_o4RgF2gn5IEz3a8WZQ_GQ&s=09", "selector": "title"}  # placeholder
}

# واجهة التحكم
col1, col2 = st.columns([1, 2])
with col1:
    selected_source = st.selectbox("🌐 اختر مصدر الأخبار:", list(rss_feeds.keys()))
    keywords_input = st.text_input("🔍 كلمات مفتاحية (مفصولة بفواصل):", "")
    keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []
    category_filter = st.selectbox("📁 اختر التصنيف:", ["الكل"] + list(category_keywords.keys()))
    date_from = st.date_input("🗓 من تاريخ:", datetime.today())
    date_to = st.date_input("🗓 إلى تاريخ:", datetime.today())
    run = st.button("📅 عرض الأخبار")

with col2:
    if run:
        news = fetch_news(
            selected_source,
            rss_feeds[selected_source],
            keywords,
            date_from,
            date_to,
            category_filter
        )

        if not news:
            st.warning("❌ لا توجد أخبار بهذه الشروط.")
        else:
            st.success(f"✅ تم العثور على {len(news)} خبر.")
            for item in news:
                with st.container():
                    st.markdown("----")
                    cols = st.columns([1, 4])
                    with cols[0]:
                        if item["image"]:
                            st.image(item["image"], use_column_width=True)
                    with cols[1]:
                        st.markdown(f"### 📰 {item['title']}")
                        st.markdown(f"🗓 التاريخ: {item['published'].strftime('%Y-%m-%d')}")
                        st.markdown(f"📁 التصنيف: {item['category']}")
                        st.markdown(f"📄 التلخيص: {summarize(item['summary'])}")
                        st.markdown(f"🎯 التحليل: {item['sentiment']}")
                        st.markdown(f"[🌐 اقرأ المزيد ↗]({item['link']})")

            def export_to_word(news_list):
                doc = Document()
                for news in news_list:
                    doc.add_heading(news['title'], level=2)
                    doc.add_paragraph(f"المصدر: {news['source']}  |  التصنيف: {news['category']}")
                    doc.add_paragraph(f"📅 التاريخ: {news['published'].strftime('%Y-%m-%d %H:%M:%S')}")
                    doc.add_paragraph(f"📄 التلخيص: {summarize(news['summary'])}")
                    doc.add_paragraph(f"🔗 الرابط: {news['link']}")
                    doc.add_paragraph(f"تحليل معنوي: {news['sentiment']}")
                    doc.add_paragraph("-----")
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                return buffer

            def export_to_excel(news_list):
                df = pd.DataFrame(news_list)
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                buffer.seek(0)
                return buffer

            st.download_button("📄 تحميل كـ Word", data=export_to_word(news), file_name="news.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            st.download_button("📊 تحميل كـ Excel", data=export_to_excel(news), file_name="news.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.markdown("### 🔠 أكثر الكلمات تكرارًا:")
            all_text = " ".join([n['summary'] for n in news])
            words = [word for word in all_text.split() if len(word) > 3]
            word_freq = Counter(words).most_common(10)
            for word, freq in word_freq:
                st.markdown(f"- **{word}**: {freq} مرة")
