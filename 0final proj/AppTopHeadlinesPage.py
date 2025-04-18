import streamlit as st
import BBCNewsScraper
import MirrorScraper
import GuardianScraper
import SkyNewsScraper
import TheSunScraper
from concurrent.futures import ThreadPoolExecutor

genreLinks = {
    "Home": ["https://feeds.bbci.co.uk/news/rss.xml", None, "https://www.thesun.co.uk", "https://www.mirror.co.uk/news/?service=rss", "https://feeds.skynews.com/feeds/rss/home.xml"],
    "World": ["https://feeds.bbci.co.uk/news/world/rss.xml", "world", "https://www.thesun.co.uk/news/worldnews", "https://www.mirror.co.uk/news/world-news/?service=rss", "https://feeds.skynews.com/feeds/rss/world.xml"],
    "Politics": ["https://feeds.bbci.co.uk/news/politics/rss.xml", "politics", "https://www.thesun.co.uk/news/politics", "https://www.mirror.co.uk/news/politics/?service=rss", "https://feeds.skynews.com/feeds/rss/politics.xml"],
    "Crime": ["https://feeds.bbci.co.uk/news/topics/cldy2dmy748t/rss.xml", "crime", "https://www.thesun.co.uk/topic/crime/", "https://www.mirror.co.uk/all-about/crime/?service=rss", "https://news.sky.com/topic/crime-9501"],
    "Entertainment":["https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "culture", "https://www.thesun.co.uk/tvandshowbiz", "https://www.mirror.co.uk/3am/?service=rss", "https://feeds.skynews.com/feeds/rss/entertainment.xml"],
}
def getHeadlines():
    loading_placeholder = st.empty()
    loading_placeholder.info("⏳ Loading articles...")

    genres = ["Home", "World", "Politics", "Crime", "Entertainment"]
    allHeadlines = {genre: {} for genre in genres}
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for genre in genres:
            links = genreLinks.get(genre)
            # Submit tasks for each news source in parallel
            futures.append((
                genre,
                "BBC News",
                executor.submit(BBCNewsScraper.getTopHeadlines, links[0])
            ))
            futures.append((
                genre,
                "The Guardian",
                executor.submit(
                    GuardianScraper.getTopHeadlines, 
                    '18daef39-58e5-4824-a400-51efa5799e43', 
                    links[1]
                )
            ))
            futures.append((
                genre,
                "The Sun",
                executor.submit(TheSunScraper.getTopHeadlines, links[2])
            ))
            futures.append((
                genre,
                "Mirror",
                executor.submit(MirrorScraper.getTopHeadlines, links[3])
            ))
            futures.append((
                genre,
                "Sky News",
                executor.submit(SkyNewsScraper.getTopHeadlines, links[4])
            ))
        
        # Collect results as they complete
        total_articles = 0
        for future in futures:
            genre, source, task = future
            try:
                allHeadlines[genre][source] = task.result()
                
            except Exception as e:
                # Handle exceptions (e.g., log the error)
                allHeadlines[genre][source] = f"Error: {str(e)}"
    
    loading_placeholder.empty()
    return allHeadlines

def filterHeadlines(genres, outlets):
    filteredHeadlines = {}
    for genre in genres:
        # Initialize an empty list for the genre
        #genre_articles = {}
        for outlet in outlets:
            # Get the articles for this outlet and genre
            articles = st.session_state.headlines.get(genre, {}).get(outlet, [])
           # genre_articles[outlet] = articles # articles [{headline, url}, headline {url}]
            filteredHeadlines[genre + ", " + outlet]=articles
    return filteredHeadlines

def setUpTopHeadlinesPage():
    # Initialize session state variables if they don't exist

    if "headlines" not in st.session_state:
        st.session_state.headlines = getHeadlines()
    
    if "selected_genres" not in st.session_state:
        st.session_state.selected_genres = ["Home"]
    
    if "selected_outlets" not in st.session_state:
        st.session_state.selected_outlets = ["BBC News", "The Guardian","The Sun", "Mirror", "Sky News"]
    
    if "filtered_headlines" not in st.session_state:
        # Apply default filters on initial load
        st.session_state.filtered_headlines = filterHeadlines(
            st.session_state.selected_genres,
            st.session_state.selected_outlets
        )

    # Create two columns for layout
    left_col, right_col = st.columns([1, 3])

    # Filter controls
    with left_col:
        # Outlet filter (show current session state values)
        with st.container(border=True):
            st.markdown("**Filter by outlet**")
            theGuardianCB = st.checkbox("The Guardian", 
                                      value="The Guardian" in st.session_state.selected_outlets)
            bbcNewsCB = st.checkbox("BBC News", 
                                   value="BBC News" in st.session_state.selected_outlets)
            theSunCB = st.checkbox("The Sun", 
                                  value="The Sun" in st.session_state.selected_outlets)
            mirrorCB = st.checkbox("Mirror", 
                                 value="Mirror" in st.session_state.selected_outlets)
            skyNewsCB = st.checkbox("Sky News", 
                                  value="Sky News" in st.session_state.selected_outlets)
        
        # Topic filter (show current session state values)
        with st.container(border=True):
            st.markdown("**Show by topic**")
            homeCB = st.checkbox("Home", 
                               value="Home" in st.session_state.selected_genres)
            worldCB = st.checkbox("World", 
                                value="World" in st.session_state.selected_genres)
            politicsCB = st.checkbox("Politics", 
                                   value="Politics" in st.session_state.selected_genres)
            crimeCB = st.checkbox("Crime", 
                                value="Crime" in st.session_state.selected_genres)
            entertainmentCB = st.checkbox("Entertainment", 
                                        value="entertainment" in st.session_state.selected_genres)

        if st.button("Apply Filters"):
            # Get selected genres from checkboxes
            new_genres = []
            if homeCB: new_genres.append("Home")
            if worldCB: new_genres.append("World")
            if politicsCB: new_genres.append("Politics")
            if crimeCB: new_genres.append("Crime")
            if entertainmentCB: new_genres.append("Entertainment")

            # Get selected outlets from checkboxes
            new_outlets = []
            if bbcNewsCB: new_outlets.append("BBC News")
            if theGuardianCB: new_outlets.append("The Guardian")
            if theSunCB: new_outlets.append("The Sun")
            if mirrorCB: new_outlets.append("Mirror")
            if skyNewsCB: new_outlets.append("Sky News")

            # Update session state with new selections
            st.session_state.selected_genres = new_genres
            st.session_state.selected_outlets = new_outlets
            
            # Filter headlines with new selections
            st.session_state.filtered_headlines = filterHeadlines(new_genres, new_outlets)

    # Always show the current filtered headlines (either initial or after apply)
    with right_col:
        displayHeadlines(st.session_state.filtered_headlines)

    # Headlines container with scroll
def displayHeadlines(headlines):
    # Headlines container with scroll
    #showing_placeholder = st.empty()
    with st.container(border=True):
        st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div[data-testid="stVerticalBlock"] {
                max-height: 70vh;
                overflow-y: auto;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the headlines
        noOfArticles = 0
        for genreOutlet, articles in headlines.items():
            genre, outlet = genreOutlet.split(", ")
            for index, article in enumerate(articles):
                noOfArticles+=1
                meta_col1, meta_col2 = st.columns([1, 1])
                with meta_col1:
                    st.caption(f"**Outlet:** {outlet}")
                with meta_col2:
                    st.caption(f"**Category:** {genre}")

                st.markdown(f"### [{article['headline']}]({article['url']})")
                col1, col2 = st.columns([1, 1])

                with col1:
                    # Copy URL button
                    if st.button("📋 Copy URL", key=f"copy{outlet}_{genre}_{index}"):
                        pass  # Add pyperclip.copy(article['url'])
                    
                
                st.divider()
        #showing_placeholder.info(f"Showing {noOfArticles} articles...")





