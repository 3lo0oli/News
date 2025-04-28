import streamlit as st
import feedparser
import pandas as pd
import io
from datetime import datetime

# -------- إعداد ديزاين CSS مخصص --------
st.markdown("""
    <style>
    /* تغيير لون الخلفية */
    .stApp {
        background-color: #0D1B2A;
        position: relative;
    }

    /* إضافة صورة الكرة الأرضية في النص */
    .background-image {
        position: absolute;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0.1;
        z-index: 0;
    }

    /* تنسيق العنوان */
    .main-title {
        color: #ffffff;
        text-align: center;
        font-size: 60px;
        margin-bottom: 50px;
        position: relative;
        z-index: 1;
    }

    /* تنسيق كل الكتابات */
    label, p, div, span {
        color: #d1d5db !important;
    }

    /* تخصيص الselectbox والtext input */
    .stTextInput > div > div, .stSelectbox > div {
        background-color: #1B263B;
        border-radius: 10px;
        color: white;
        border: 1px solid #415A77;
        padding: 8px;
    }

    /* تخصيص الزر */
    button[kind="primary"] {
        background-color: #415A77;
        color: white;
        font-size: 18px;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
    }
    </style>

    <!-- هنا بنضيف صورة الكرة الأرضية -->
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Earth_Western_Hemisphere_transparent_background.png/600px-Earth_Western_Hemisphere_transparent_background.png" class="background-image" width="300">
""", unsafe_allow_html=True)

# -------- Streamlit App --------
st.markdown("<h1 class='main-title'>Bravo News 👌</h1>", unsafe_allow_html=True)

# قائمة التصنيفات
rss_feeds = {
    "BBC عربي": "http://feeds.bbci.co.uk/arabic/rss.xml",
    "CNN بالعربية": "http://arabic.cnn.com/rss/latest",
    "RT Arabic": "https://arabic.rt.com/rss/",
    "France24 عربي": "https://www.france24.com/ar/rss",
    "الشرق الأوسط": "https://aawsat.com/home/rss.xml"
}

# اختيار التصنيف
selected_feed = st.selectbox("اختر مصدر الأخبار:", list(rss_feeds.keys()))

# إدخال رابط مخصص
custom_rss = st.text_input("🛠️ مخصص لتغذية الأخبار (اختياري):")

# إدخال الكلمات المفتاحية
keywords_input = st.text_input("🔎 بحث الكلمات المفتاحية (اختياري):")
keywords = [kw.strip() for kw in keywords_input.split(",")] if keywords_input else []

# -------- استخراج الأخبار --------
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
