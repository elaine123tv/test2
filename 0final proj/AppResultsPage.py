import streamlit as st
import pandas as pd
import plotly.express as px
import BiasAnalyser

def displaySingleArticle(gpt_data, textblob_data, gpt_checked, textblob_checked):
    st.subheader("Detailed Analysis")
    
    if gpt_checked:
        with st.container(border=True):
            st.markdown("### GPT Analysis")
            
            cols = st.columns(4)
            cols[0].metric("Title Objectivity", f"{gpt_data['titleObjectivityValue']:.2f}")
            cols[1].metric("Title Polarity", f"{gpt_data['titlePolarityValue']:.2f}")
            cols[2].metric("Title Lean", f"{gpt_data['titleLeanValue']:.2f}")
            
            with st.expander("Title Objectivity Reason"):
                st.write(gpt_data['titleObjectivityReason'])
            with st.expander("Title Lean Explanation"):
                st.write(gpt_data['titleLean'])
            
            st.divider()
            
            cols = st.columns(4)
            cols[0].metric("Body Objectivity", f"{gpt_data['bodyObjectivityValue']:.2f}")
            cols[1].metric("Body Polarity", f"{gpt_data['bodyPolarityValue']:.2f}")
            cols[2].metric("Body Lean", f"{gpt_data['bodyLeanValue']:.2f}")
            
            with st.expander("Body Objectivity Reason"):
                st.write(gpt_data['bodyObjectivityReason'])
            with st.expander("Body Lean Explanation"):
                st.write(gpt_data['bodyLean'])

    if textblob_checked:
        with st.container(border=True):
            st.markdown("### TextBlob Analysis")
            
            if textblob_data['titlePolarity'] is not None:
                st.write("**Title Polarity Scores:**")
                cols = st.columns(4)
                cols[0].metric("Title", f"{textblob_data['titlePolarity']:.2f}")
                cols[1].metric("Body", f"{textblob_data['titlePolarity']:.2f}")
            
            if textblob_data['bodyPolarity'] is not None:
                st.write("**Content Polarity Scores:**")
                cols = st.columns(4)
                cols[0].metric("Title", f"{textblob_data['bodyPolarity']:.2f}")
                cols[1].metric("Body", f"{textblob_data['bodyPolarity']:.2f}")


def displayMultipleArticles(articles, gpt_analyses, textblob_analyses, gpt_checked, textblob_checked):
    # Create dataframe with analysis data (existing code remains the same)
    data = []
    for idx, (article, gpt, tb) in enumerate(zip(articles, gpt_analyses, textblob_analyses)):
        entry = {
            'Article': f'Article {idx+1}',
            'Outlet': article.get('outlet', 'Unknown'),
            'Title Objectivity (GPT)': gpt['titleObjectivityValue'],
            'Title Lean (GPT)': gpt['titleLeanValue'],
            'Title Polarity (GPT)': gpt['titlePolarityValue'],
            'Body Objectivity (GPT)': gpt['bodyObjectivityValue'],
            'Body Lean (GPT)': gpt['bodyLeanValue'],
            'Body Polarity (GPT)': gpt['bodyPolarityValue'],
            'Title Polarity (TB)': tb['titlePolarity'] ,
            'Content Polarity (TB)': tb['bodyPolarity']
        }
        data.append(entry)
    
    df = pd.DataFrame(data)
    
    # Grouping controls (existing code remains the same)
    group_mode = st.radio("Analysis Mode:", ["By Article", "By Outlet"], index=0)
    
    if group_mode == "By Outlet":
        outlets = df['Outlet'].unique()
        if len(outlets) > 1:
            agg_dict = {
                'Title Objectivity (GPT)': 'mean',
                'Title Lean (GPT)': 'mean',
                'Title Polarity (GPT)': 'mean',
                'Body Objectivity (GPT)': 'mean',
                'Body Lean (GPT)': 'mean',
                'Body Polarity (GPT)': 'mean',
                'Title Polarity (TB)': 'mean',
                'Content Polarity (TB)': 'mean'
            }
            df = df.groupby('Outlet').agg(agg_dict).reset_index()
            x_axis = 'Outlet'
        else:
            st.warning("All articles are from the same outlet")
            group_mode = "By Article"
    
    if group_mode == "By Article":
        x_axis = 'Article'

    # Corrected Visualization Section
    if gpt_checked:
        st.markdown("## GPT Analysis Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            # Fixed x-axis parameter
            fig = px.bar(df, x=x_axis, y=['Title Objectivity (GPT)', 'Body Objectivity (GPT)'], 
                         title="Objectivity Comparison", barmode='group')
            st.plotly_chart(fig)
        
        with col2:
            # Fixed x-axis parameter
            fig = px.bar(df, x=x_axis, y=['Title Lean (GPT)', 'Body Lean (GPT)'], 
                         title="Political Lean Comparison", barmode='group')
            st.plotly_chart(fig)
        
        # Scatter plot remains the same
        fig = px.scatter(df, x='Title Polarity (GPT)', y='Body Polarity (GPT)', 
                         color=x_axis, size_max=20,
                         title="Title vs Body Sentiment (GPT)")
        st.plotly_chart(fig)

    if textblob_checked:
        st.markdown("## TextBlob Analysis Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            # Existing correct implementation
            fig = px.bar(df, x=x_axis, y='Title Polarity (TB)', 
                         title="Title Polarity (TextBlob)")
            st.plotly_chart(fig)
        
        with col2:
            # Existing correct implementation
            fig = px.bar(df, x=x_axis, y='Content Polarity (TB)', 
                         title="Content Polarity (TextBlob)")
            st.plotly_chart(fig)

def displayResults():
    fieldsData = st.session_state.get('fieldsData')
    print(fieldsData)
    # Handle data format
    if isinstance(fieldsData, dict):
        articles = [fieldsData]
    elif isinstance(fieldsData, list):
        articles = fieldsData
    else:
        st.error("Invalid data format")
        return
    
    # Process analyses
    gpt_analyses = [BiasAnalyser.gptAnalysis(article) for article in articles]
    textblob_analyses = [BiasAnalyser.textBlobAnalysis(article) for article in articles]
    
    # Analysis toggle
    col1, col2 = st.columns(2)
    with col1:
        gpt_checked = st.checkbox("Show GPT Analysis", value=True)
    with col2:
        textblob_checked = st.checkbox("Show TextBlob Analysis", value=True)
    
    # Main display logic
    if len(articles) == 1:
        displaySingleArticle(gpt_analyses[0], textblob_analyses[0], gpt_checked, textblob_checked)
        print("Single article analysis NO MYLRIPLW")
    else:
        displayMultipleArticles(articles, gpt_analyses, textblob_analyses, gpt_checked, textblob_checked)

    with st.expander("View Raw Analysis Data"):
        st.write("GPT Analysis Results:", gpt_analyses)
        st.write("TextBlob Analysis Results:", textblob_analyses)