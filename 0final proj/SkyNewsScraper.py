import feedparser
import lxml
import requests
from bs4 import BeautifulSoup
import re
import newspaper
import WebScraper

def getTopHeadlines(homeUrl):
    topHeadlines = []
    if homeUrl in["https://news.sky.com/topic/crime-9501", "https://news.sky.com/politics"]:
        response = requests.get(homeUrl)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if soup.find('div', class_="ui-story-content"):
                articles = soup.find_all('div', class_="ui-story-content")
                for article in articles:
                    if article.find('a', href=True)['href'] and article.find('a')["data-title"] and not "/video" in article.find('a', href=True)['href'] :
                        topHeadlines.append({
                            'headline': article.find('a')["data-title"],
                            'url': "https://news.sky.com"+article.find('a', href=True)['href'],
                        })
    else:
        feed = feedparser.parse(homeUrl)
        topHeadlines.extend(
            {
                'headline': entry.title,
                'url': entry.link
            }
            #for entry in feed.entries[:10]
            for entry in feed.entries[:10]
        )
    return topHeadlines
        

def getArticleData(articleUrl):
    response = requests.get(articleUrl)

    if response.status_code == 200:
        # title 0, subtitle 1, body 2, captions3 , link 4
        title = ""
        subTitle = ""
        contentList = []
        captions = []

        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find('h1'):      
            title = soup.find('h1').get_text()
        if soup.find('p', class_="sdc-article-header__sub-title sdc-site-component-header--h2"):
            subTitle = soup.find('p', class_="sdc-article-header__sub-title sdc-site-component-header--h2").get_text()
        if soup.find('div', class_="sdc-article-body sdc-article-body--story sdc-article-body--lead"):
            div = soup.find('div', class_="sdc-article-body sdc-article-body--story sdc-article-body--lead")
            if div.find('p'):
                for p in div.find_all('p'):
                    if p.find_parent("div") == div and "Read more:" not in p.get_text(): #remove related stories
                        if(p.find('strong')):
                            if not p.find('strong').find('a'):
                                contentList.append("\n" + p.get_text() + "\n" + "\n")
                        else:
                            contentList.append(p.get_text() + "\n")
                        
            if soup.find('span', class_="ui-media-caption__caption-text"):
                for caption in soup.find_all('span', class_="ui-media-caption__caption-text"):
                    if "Pic:" or "file Pic:"in caption.get_text():
                        captions.append(re.sub(r'Pic:.*', '', caption.get_text().strip()))
                    else:
                        captions.append(caption.get_text.strip())
        else:
            contentList = "newspaper4k " + newspaper.article(articleUrl).text

        content = "".join(contentList)
        articleData = {
            "title": title.get_text(),
            "subTitle": subTitle,
            "content": content,
            "captions": captions,
            #"links": links
        }
        return articleData





#getTopHeadlineUrls("https://feeds.skynews.com/feeds/rss/home.xml")
#getArticleData("https://news.sky.com/story/baltic-countries-cut-off-russian-energy-supply-13305132")

"""urls = getTopHeadlines("https://feeds.skynews.com/feeds/rss/home.xml")
print(urls)"""