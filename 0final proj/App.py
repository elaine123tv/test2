import streamlit as st
from AppTopHeadlinesPage import setUpTopHeadlinesPage
from AppAnalysePage import displayAnalyse
from AppResultsPage import displayResults

# Configure page settings
st.set_page_config(page_title="UK News Bias Detector", layout="wide")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'TopHeadlines'

# Main header
st.markdown(
    "<h1 style='text-align: center;'>📰 UK News Bias Detector</h1>", 
    unsafe_allow_html=True
)

# Navigation controls centered at top
nav_options = ["TopHeadlines", "Analyse", "Results"]
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <style>
            div[role="radiogroup"] {
                display: flex;
                justify-content: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Get current page index to set radio default
    try:
        current_index = nav_options.index(st.session_state.page)
    except ValueError:
        current_index = 0  # Fallback to first option if invalid

    # Radio widget updates page directly
    selected_page = st.radio(
        "Navigation",
        nav_options,
        index=current_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Update page state if radio selection changes
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()  # Force immediate rerun to update page

# Page routing
if st.session_state.page == 'TopHeadlines':
    setUpTopHeadlinesPage()
elif st.session_state.page == 'Analyse':
    displayAnalyse()
elif st.session_state.page == 'Results':
    displayResults()