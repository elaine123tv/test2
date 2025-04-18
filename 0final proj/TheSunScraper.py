import requests
from bs4 import BeautifulSoup
import re
import newspaper
import WebScraper

def getTopHeadlines(homeUrl):
    
    response = requests.get(homeUrl)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', class_ = "teaser__copy-container")
                
        headlines = []

        for div in divs[:10]:
            news = div.find('h3')
            link = div.find('a')
            if news and link and link.get('href'):
                headlines.append({
                    'headline': news.get_text(),
                    'url': link['href']
                })
    
        return headlines

def getArticleData(articleUrl):

    response = requests.get(articleUrl)

    if response.status_code == 200:
        title = ""
        subTitle = ""
        contentList = []
        captions = []

        soup = BeautifulSoup(response.content, 'html.parser')
        # title = soup.find('h1').get_text().strip()
        
        if soup.find('div', class_="article__subdeck t-p-border-color"):
            subTitle = soup.find('div', class_="article__subdeck t-p-border-color").get_text()

        if soup.find('div', class_="article__content"):
            article = soup.find('div', class_ = "article__content")
            if article.find_all(['p', 'h2']):
                paragraphs = article.find_all(['p', 'h2'])
                for p in paragraphs:
                    if p.find('a') and p.find('a')['href'].startswith("https://link.thesun.co.uk/join/"):
                        continue
                    elif p.name.startswith("h"): # if subheading
                        if p.get("class") not in [["read-more-container_title"], ["rail-stacked_anchor-heading_h2"]]:
                            contentList.append("\n" + p.get_text() + "\n" + "\n")
                    else:
                        contentList.append(p.get_text() + "\n")

            if article.find_all('span', class_="article__media-span"):
                spans = soup.find_all('span', class_="article__media-span")
                captions.extend(span.get_text() for span in spans)
        else:
            if newspaper.article(articleUrl):
                contentList = "newspaper4k " + newspaper.article(articleUrl).text
            else: 
                contentList=""
        content = "".join(contentList)
        articleData = {
            "title": title,
            "subTitle": subTitle,
            "content": content,
            "captions": captions,
        }
        return articleData



#getTopHeadlineUrls("https://www.thesun.co.uk/news/politics")
#etArticleData("https://www.thesun.co.uk/news/33524382/starmer-macron-trump-ukraine-trip/")
#clean(getArticleData("https://www.bbc.co.uk/news/articles/cm2m1ey10rxo"))
#clean(getArticleData("https://www.thesun.co.uk/news/33239679/trump-sanctions-international-criminal-court-icc/"))
'''urls = getHomeTopHeadlineUrls()
for url in getHomeTopHeadlineUrls():
    getArticleData(url)'''