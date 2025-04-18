import re
import newspaper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import feedparser
import WebScraper

def getTopHeadlines(homeUrl):
    headlines = []
    """response = requests.get(homeUrl)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_=lambda c: c and c.startswith("story story"))

        for article in articles:
            if len(headlines) >= 10:  # Stop when 10 headlines are collected
                break
            # Extract the headline text and URL from the anchor tag

            link = article.find('a')
            if link and link.get('href'):
                headlines.append({
                    'headline': link.get_text().strip(),
                    'url': link['href']
                })"""
        
        # Print results
    feed = feedparser.parse(homeUrl)
    headlines.extend(
        {
            'headline': entry.title,
            'url': entry.link
        }
        #for entry in feed.entries[:10]
        for entry in feed.entries[:10]
    )
    return headlines 

def getArticleData(articleUrl):
    
    response = requests.get(articleUrl)
    if response.status_code == 200:
        deleteText = "At Reach and across our entities we and our partners use information collected through cookies and other identifiers from your device to improve"
        # title 0, subtitle 1, body 2, captions3 , link 4
        title = ""
        subTitle = ""
        contentList=[]
        captions = []

        soup = BeautifulSoup(response.content, 'html.parser')

        if soup.find('h1'):
            title = soup.find('h1').get_text()
        
        if soup.find('h2'):
            subTitle = soup.find('h2').get_text()

        if soup.find_all('span', class_=lambda c: c and 'caption-title' in c):
            spans = soup.find_all('span', class_=lambda c: c and 'caption-title' in c)
            for span in spans:
                captions.append(span.get_text())
        if soup.find("article", id_="article-body") and soup.find(p, class_="Paragraph_paragraph-text__PVKlh"):
            paragraphs = soup.find_all('p',class_="Paragraph_paragraph-text__PVKlh")
            for p in paragraphs:
                if not deleteText in p.get_text() and not p.find_parent('aside') and not p.find_parent('div', class_=re.compile(r'factbox', re.I)) and not p.find_parent('form') and not p.find_parent('email-slide-in'):
                    if p.find('strong') and not p.find('em'):
                        contentList.append("\n" + p.get_text() + "\n" + "\n")
                    else:
                        contentList.append(p.get_text() + "\n")
        elif soup.find('p'):
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                if not deleteText in p.get_text() and not p.find_parent('aside') and not p.find_parent('div', class_=re.compile(r'factbox', re.I)) and not p.find_parent('form') and not p.find_parent('email-slide-in'):
                    if p.find('strong') and not p.find('em'):
                        contentList.append("\n" + p.get_text() + "\n" + "\n")
                    else:
                        contentList.append(p.get_text() + "\n")
        else:
            contentList = "newspaper4k " + newspaper.article(articleUrl).text

        content = "".join(contentList)

        articleData = {
            "title": title,
            "subTitle": subTitle,
            "content": content,
            "captions": captions,
            #"links": links
        }
        

    return articleData
    
##getTopHeadlineUrls('https://www.mirror.co.uk/')
#getTopHeadlineUrls('https://www.mirror.co.uk/news/politics/')
#getTopHeadlineUrls('https://www.mirror.co.uk/all-about/ufc')
#getArticleData('https://www.mirror.co.uk/news/politics/7-unsettling-things-donald-trump-34729973')

'''urls = getHomeTopHeadlineUrls()
for url in getHomeTopHeadlineUrls():
    getArticleData(url)'''
#getArticleData("https://www.mirror.co.uk/money/uk-hit-donald-trumps-global-34847675")