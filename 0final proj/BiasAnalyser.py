import json
import re

import newspaper
from openai import OpenAI
from textblob import TextBlob
import BBCNewsScraper
import GuardianScraper
import MirrorScraper
import SkyNewsScraper
import TheSunScraper
import string
import nltk
import contractions
import pandas as pd

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import time

"""def combineMLDatasets():
    
    bbcDS1 = pd.read_csv("bbc.csv")
    
    bbcDS1.drop('Topic', axis=1, inplace=True)
    
    bbcDS2 = pd.read_csv("bbc4.csv")

    bbcCombined = pd.concat([bbcDS1, bbcDS2], axis=1)

    guardianDS1=pd.read_csv("guardian.csv")
    guardianDS1.columns = ['Headlines', 'URLs']
    guardianDS1.insert(0, 'Outlet', 'The Guardian')
    guardianDS2=pd.read_csv("guardian2.csv")
    guardianDS2.drop('urls', axis=1, inplace=True)
    guardianCombined = pd.concat([guardianDS1, guardianDS2], axis=1)

    theSunDS1 = pd.read_csv("theSun.csv")
    theSunDS1['Outlet'] = 'The Sun'
    theSunDS1['URLs'] = "https://www.thesun.co.uk" +theSunDS1['URLs']
    theSunDS2 = pd.read_csv("theSun3.csv")
    theSunCombined = pd.concat([theSunDS1, theSunDS2], axis=1)

    mirrorDS1 = pd.read_csv("mirror1.csv")
    mirrorDS1.columns = ['Headlines', 'URLs']
    mirrorDS1.insert(0, 'Outlet', 'Mirror')
    mirrorDS2 = pd.read_csv("mirror2.csv")
    mirrorCombined = pd.concat([mirrorDS1, mirrorDS2], axis=1)

    skyDS = pd.read_csv("skyNews.csv")
    dataset = pd.concat([bbcCombined, guardianCombined, theSunCombined, mirrorCombined, skyDS], axis=0, ignore_index=True)
    dataset.to_csv("MLDataset.csv", index=False)

def cleanMLDS():
    df = pd.read_csv("MLDataset.csv")
    linksToRemove = ['https://www.bbc.co.uk/news/videos', 'https://www.bbc.co.uk/sounds', 'https://www.bbc.co.uk/news/live', 'https://www.bbc.co.uk/iplayer']
    df = df[~df['URLs'].apply(lambda x: any(x.startswith(link) for link in linksToRemove))]
    df = df[~df['Content'].str.startswith('newspaper4k ', na=False)]
    df['Captions'] = df['Captions'].str.replace('Image caption, ', '', regex=False)
    df['Captions'] = df['Captions'].str.replace('Media caption, ', '', regex=False)

    df.to_csv("MLDataset.csv", index=False)"""

def clean(articleData, includeQuotes):

    punctuation_list = list(string.punctuation)

    for key, value in articleData.items():
        if key in ["title", "subTitle", "content"]:
            newValue = value

            newValue = re.sub(r'http[s]?://\S+|www\.\S+', '', newValue)
    
            # Remove email addresses (including .co.uk, .com, etc.)
            newValue = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:com|org|net|edu|gov|co\.uk|co|io|info|biz)\b', '', newValue)

            # standardise quotes
            newValue = newValue.replace("“", '"').replace("”", '"')

            # remove numbers, special chars except quotation marks
            newValue = re.sub(r'[^A-Za-z\s\'"]', '', newValue)

            # handling contractions#
            newValue = contractions.fix(newValue)
            newValue = newValue.replace("'s", " ")

            # if remove quotes
            if not includeQuotes:
                # Check if quotes are uneven
                quoteMarks = newValue.count("'")
                quoteMarks+= newValue.count('"')
                if quoteMarks and quoteMarks % 2 != 0:
                    print(f"⚠️ Warning: Uneven number of quotation marks ({quoteMarks}) in text.")

                # remove quotes
                newValue = re.sub(r'"(.*?)"', ' ', newValue)
                newValue = re.sub(r"'(.*?)'", ' ', newValue)

            # remove punctuation
            for punctuation in punctuation_list:
                newValue = newValue.replace(punctuation,  " ")

            # remove whitespace
            newValue = newValue.strip()
            
            if "US" in newValue:
                newValue = newValue.replace("US", "USA") # lemmatizer treating US as a plural noun, lematizing it to u
            tokens = word_tokenize(newValue.lower())

            # remove stopwords (e.g.  "the", "a")
            filteredTokens = [token for token in tokens if token not in stopwords.words('english') or token == "US"]
            
            # Reduce words to their base or root form to handle different variations of a word. e.g. "running -> run"
            lemmatizer = WordNetLemmatizer()
            lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filteredTokens]

            newValue = ' '.join(lemmatized_tokens)



            articleData[key] = newValue
        

    return articleData

def textBlobAnalysis(articleData):
    newContent = articleData["subTitle"] + " " + articleData["content"]
    for caption in articleData["captions"]:
        newContent+=" " + caption

    blob = TextBlob(articleData['title'])
    print("title: " + articleData['title'])
    blob2 = TextBlob(newContent)

    sentiment = blob.sentiment
    sentiment2 = blob2.sentiment
    analysis = {
        "titlePolarity": sentiment.polarity if articleData["title"] else "",
        "titleObjectivity": sentiment.subjectivity if articleData["title"] else "",
        "bodyPolarity": sentiment2.polarity if newContent else "",
        "bodyObjectivity": sentiment2.subjectivity if newContent else "",
    }
    return analysis

def nltkPolarityAnalysis(articleData):
    newContent = articleData["subTitle"] + " " + articleData["content"]
    for caption in articleData["captions"]:
        newContent+=" " + caption
    analyzer = SentimentIntensityAnalyzer()


    analysis = {
        "titlePolarity": analyzer.polarity_scores(articleData['title']) if articleData["title"] else "",
        "contentPolarity": analyzer.polarity_scores(newContent) if newContent else "",
    }

    return analysis

def gptAnalysis(articleData):

    apiKey = "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"
    if "Captions" in articleData:
        captions = "Captions:" + articleData["Captions"]
    else:
        captions = ""
    if "Sub Titles" in articleData:
        subTitle = articleData["Sub Titles"]
    else:
        subTitle = ""
    
    with open(r'C:\Users\Boss (Dia)\OneDrive - Liverpool John Moores University\0final proj\llmBiasDetectorPrompt.txt', 'r') as file:
            promptTemplate = file.read()

    prompt = promptTemplate.format(insertTitle = articleData['title'],insertSubTitle=subTitle, insertContent=articleData['content'], insertCaptions=captions)
    print(prompt)
    client = OpenAI(api_key=apiKey)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a news bias and sentiment detector."},
            {"role": "user", "content": prompt},
        ]
    )
    content = response.choices[0].message.content
    results = json.loads(content)

    return results

def gptDSFill():
    apiKey = "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"
    df = pd.read_csv('MLDataset_AutoSave.csv')
    """df["Bias"] = None
    df["Political Leaning"] = None
    df["Sentiment"] = None"""
    
    
    client = OpenAI(api_key=apiKey)
    start_time = time.time()  # Record the start time
    startIndex = 6902
    for index, row in df.iloc[startIndex:].iterrows():  # Start from 6902 for index, row in df.iloc[startIndex:].iterrows():
        article = f"Headline: {df['Headlines'].iloc[index]}\n\n"

        if pd.notna(df['Sub Titles'].iloc[index]):
            article += f"Sub title: {df['Sub Titles'].iloc[index]}\n""\n"
        
        article += f"Body: {df['Content'].iloc[index]}\n""\n"
        
        if pd.notna(df['Captions'].iloc[index]):
            article += f"Captions: {df['Captions'].iloc[index]}\n""\n"

        with open('llmLabelDatasetPrompt.txt', 'r') as file:
            promptTemplate = file.read()

        prompt = promptTemplate.format(insert_article = article)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an unbiased news article reviewer."},
                    {"role": "user", "content": prompt},
                ]
            )
            content = response.choices[0].message.content
            results = json.loads(content)
            df.at[index, "Bias"] = results['bias']
            df.at[index, "Political Leaning"] = results['politicalLeaning']
            df.at[index, "Sentiment"] = results['sentiment']
            print(index)

        except Exception as e:
            print(f"Unexpected error: {e}. Saving DataFrame and exiting.")
            df.to_csv("MLDataset_with_errors.csv", index=False)

        if time.time() - start_time >= 600:
            df.to_csv("MLDataset_AutoSave.csv", index=False)
            print("Auto-saved progress at index:", index)
            start_time = time.time()  # Reset the timer
    df.to_csv("MLDatasetLabelled.csv", index=False)

#def fineTuneBert():


#print(textBlobAnalysis(clean(BBCNewsScraper.getArticleData("https://www.bbc.co.uk/news/articles/cly44r4pvd5o"), False)))
#print(nltkPolarityAnalysis(clean(BBCNewsScraper.getArticleData("https://www.bbc.co.uk/news/articles/cly44r4pvd5o"), False)))

#results = gptAnalysis(BBCNewsScraper.getArticleData("https://www.bbc.co.uk/news/articles/cly44r4pvd5o"))
#print(GuardianScraper.getTopHeadlines('18daef39-58e5-4824-a400-51efa5799e43', "crime"))
#print(GuardianScraper.getArticleData2('https://www.theguardian.com/uk-news/2025/mar/16/number-uk-asylum-seekers-awaiting-appeals-up-two-years'))

#textBlobAnalysis(BBCNewsScraper.getArticleData("https://www.bbc.co.uk/news/articles/cly44r4pvd5o"))
#print(SkyNewsScraper.getTopHeadlines("https://news.sky.com/topic/crime-9501"))
#print(TheSunScraper.getArticleData("https://www.thesun.co.uk/news/33873544/start-the-job-hunt-in-class/"))
#print("newspaper4k " + newspaper.article("https://www.theguardian.com/artanddesign/2025/mar/17/polynesians-astonishing-revelations-paul-gauguin-syphilis-underage").text)
#print(GuardianScraper.getArticleData2("https://www.theguardian.com/politics/live/2024/feb/02/labour-28bn-green-investment-pledge-keir-starmer-rachel-reeves-uk-politics-live"))
#print(BBCNewsScraper.getArticleData("https://www.bbc.co.uk/news/articles/cwygx918vneo")["content"])
#print(TheSunScraper.getArticleData("https://www.thesun.co.uk/news/25397979/the-suns-second-news-briefing/"))
#print(SkyNewsScraper.getArticleData("https://news.sky.com/story/a-labour-party-in-tory-clothing-why-starmers-backbenchers-are-deeply-uncomfortable-13330162")["content"])
# combineMLDatasets()
#cleanMLDS()
# df = pd.DataFrame(pd.read_csv("MLDataset.csv"))
"""print(df.head(10))
print(df.shape)"""

#sky, bbcnews, sun, sky"""
#gptDSFill()