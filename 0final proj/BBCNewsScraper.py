import requests
from bs4 import BeautifulSoup
import re
import feedparser
import newspaper

def getTopHeadlines(homeUrl):
    
    """response = requests.get(homeUrl)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('li', class_=re.compile(r'.*e1gp961v0'))
        articles.extend(soup.find_all('div', class_=re.compile(r'^ssrcss-tq7xfh-PromoContent'))) #class="ssrcss-tq7xfh-PromoContent exn3ah913"
        topHeadlines = [
            {
                "headline": article.find('p', class_=re.compile("PromoHeadline")).get_text(),
                "url": 'https://www.bbc.co.uk' + article.find('a')['href']
            }
            for article in articles[:10] if article.find('a') and article.find('p', class_=re.compile("PromoHeadline"))
        ]
        return topHeadlines"""
    topHeadlines=[]
    feed = feedparser.parse(homeUrl)
    topHeadlines.extend(
        {
            'headline': entry.title,
            'url': entry.link
        }
        for entry in feed.entries[:10]
    )
    return topHeadlines


def getArticleData(articleUrl):

    response = requests.get(articleUrl)

    if response.status_code == 200:

        # title 0, subtitle 1, body 2, captions3 , link 4
        title = ""
        subTitle = ""
        contentList=[]
        captions = []
        links = []

        soup = BeautifulSoup(response.content, 'html.parser')


        if soup.find('main'):
            article = soup.find('main')
            if article.find_all('a'):
                anchors = article.find_all('a')
        
            if soup.find('h1') :
                if isinstance(soup.find('h1'), str):  # If it's a string, use it directly
                    title = soup.find('h1')
                else:  # If it's a tag, extract the text
                    title = soup.find('h1').get_text()
            #components = article.find_all('div')
            
            for div in article.find_all('div', class_='ssrcss-1le81vw-ListContainer e5tfeyi0'):
                div.decompose()  # Removes the unwanted div and its content

            for component in article.find_all('div'):
                # if return empty
                if component.get('data-component') in ['image-block', 'video-block', 'media-block']:
                    if component.find('figcaption'):
                        captions.append( component.find('figcaption').get_text())

                if component.get('data-component') in ['text-block', 'subheadline-block', 'text-blob']:
                    #content.append(component.get_text())
                    if component.find('a') and component.find('a')['href'].startswith("/newsletters"):
                        continue
                    if component.find('h2'):
                        for h2 in component.find_all('h2'):
                            contentList.append("\n"+ h2.get_text() + "\n" +"\n")
                    if component.find('p'):
                        for p in component.find_all('p'):
                            if not p.find('i'):
                                
                                if p.find('b', class_="ssrcss-1xjjfut-BoldText e5tfeyi3"):
                                    subTitle = p.find('b', class_="ssrcss-1xjjfut-BoldText e5tfeyi3").get_text()
                                else: 
                                    contentList.append(p.get_text() + "\n")

                """elif component.find('p', class_="ssrcss-1q0x1qg-Paragraph e1jhz7w10"): # for live
                    paragraphs = component.find_all('p', class_="ssrcss-1q0x1qg-Paragraph e1jhz7w10")
                    contentList.extend(
                        p.get_text() + '\n' for p in paragraphs
                    )"""
            content = ''.join(contentList)
            if content == "":
                content = "newspaper4k " + newspaper.article(articleUrl).text
        else:
            content = "newspaper4k " + newspaper.article(articleUrl).text
        articleData = {
            "title": title,
            "subTitle": subTitle,
            "content": content,
            "captions": captions,
        }
    
        return articleData
    



getTopHeadlines("https://www.bbc.co.uk/news/rss.xml")
