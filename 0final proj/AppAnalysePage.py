import re
import streamlit as st
import BBCNewsScraper
import TheSunScraper
import MirrorScraper
import SkyNewsScraper
import GuardianScraper

scraperMap = {
        "https://www.bbc.co.uk/news/live/":BBCNewsScraper,
        "https://www.bbc.co.uk/news/articles/":BBCNewsScraper,
        "https://www.thesun.co.uk/":TheSunScraper,
        "https://www.mirror.co.uk/":MirrorScraper,
        "https://news.sky.com/story/":SkyNewsScraper,
        "https://www.theguardian.com/":GuardianScraper
}

def displayAnalyse():
    st.session_state.fieldsData = []
    st.subheader("Article Analysis")
    
    # Initialize session state for input fields
    if 'input_fields' not in st.session_state:
        st.session_state.input_fields = []

    # Input type selector
    col1, col2, _ = st.columns([2, 2, 6])
    with col1:
        if st.button("➕ Add URL", use_container_width=True):
            st.session_state.input_fields.append({"type": "url", "link": "", "num":""})
    with col2:
        if st.button("📄 Add Article", use_container_width=True):
            st.session_state.input_fields.append({"type": "article", "title": "", "body": "", "num":""})

    # Display input fields
    input_container = st.container(border=True)
    with input_container:
        for i, field in enumerate(st.session_state.input_fields):
            col1, col2 = st.columns([10, 1])
            with col1:
                if field["type"] == "url":
                    field["link"] = st.text_input(
                        f"Article {i+1} URL", 
                        value=field["link"], 
                        placeholder="Insert URL...", 
                        key=f"url_{i}"
                    )
                    field["num"] = i+1
                elif field["type"] == "article":
                    field["title"] = st.text_input(
                        f"Article {i+1} Title",
                        value=field["title"],
                        placeholder="Insert article title...",
                        key=f"title_{i}"
                    )
                    field["body"] = st.text_area(
                        f"Article {i+1} Body",
                        value=field["body"],
                        placeholder="Insert article body...",
                        height=200,
                        key=f"body_{i}"
                    )
                    field["num"] = i+1
            with col2:
                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.input_fields.pop(i)
                    st.rerun()

    # Analysis button
    if st.button("🔍 Analyse Article", type="primary"):
        fieldsData = []
        errors = []
        for field in st.session_state.input_fields:
            if field["type"] == "url":
                scraper = checkURLField(field["link"])
                if scraper is False:
                    errors.append(f"Article {field['num']} has an invalid URL. Please ensure it is a valid news article URL from one of the 5 news outlets.")
                else:
                    data = scraper.getArticleData(field["link"])
                    if data:
                        fieldsData.append(data)
                
            elif field["type"] == "article":
                if checkArticleFields(field["title"], field["body"]) is False:
                    errors.append(f"Article {field['num']} needs both title or/and body.")
                    
                else:
                    fieldsData.append({
                        "type": "article",
                        "title": field["title"],
                        "content": field["body"]
                    })
        if errors:
            for error in errors:
                st.error(error)

        else:
            st.session_state.fieldsData = fieldsData
            st.session_state.page = 'Results'  
            st.rerun()  

def checkURLField(url):
    for key, scraper in scraperMap.items():
        if url.startswith(key):
            return scraper
    else:
        return False 


def checkArticleFields(title, content):
    if not title or not content:
        return False  # One of them is empty

    if not re.search(r'[a-zA-Z]+', title) or not re.search(r'[a-zA-Z]+', content):
        return False  

    return True