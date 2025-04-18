import re
from bs4 import BeautifulSoup
import requests
import newspaper

def getTopHeadlines(api_key, section):
    results = []
    if section=="crime":
        response = requests.get("https://www.theguardian.com/uk/ukcrime")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('div', class_="dcr-f9aim1")
            results.extend(
                {
                    'headline': article.find('h3').get_text(),
                    'url': "https://www.theguardian.com"+article.find('a', href=True)['href'],
                }
                for article in articles[:10]
            )
    else:
        base_url = "https://content.guardianapis.com/search"
        params = {
            'api-key': api_key,
            'page-size': 10,
            'show-fields': 'headline,trailText,byline',
            'show-tags': 'keyword',
        }

        # if genre selected dcr-f9aim1
        if section:
            params['section'] = section
        
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print("Failed to retrieve data")
            return []
        
        data = response.json()
        articles = data['response']['results']
        
        
        results.extend(
            {
                'headline': article['fields']['headline'],
                'url': article['webUrl'],
            }
            for article in articles
        )
    
    return results

def getArticleData(api_key, article_url):
    
    base_url = article_url.replace("www.theguardian","content.guardianapis")
    params = {
        'api-key': api_key,
        'show-fields': 'body,headline,trailText,main',
        'show-elements': 'all'
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Failed to retrieve article data")
        return None
    
    # title 0, subtitle 1, body 2, captions, link
    title = ""
    subTitle = ""
    content=""
    captions = {}
    #links = []

    data = response.json()
   
    article = data['response']['content']
    title = article['fields']['headline']
    body_html = article['fields']['body']
    subTitle = article['fields']['trailText']
    soup = BeautifulSoup(body_html, "html.parser")
 
    """anchors = soup.find_all('a')
    for a in anchors:
        href = a.get('href')
        if not "mailto:" in href:
            links.append(a.get('href'))"""

    body = soup.get_text()

    articleData = {
        "title": title,
        "url":article_url,
        "subTitle": subTitle,
        "content": "api " + body,
        "captions": captions,
        #"links": links
    }
    return articleData

def getArticleData2(articleUrl):

    response = requests.get(articleUrl)
    
    if response.status_code == 200:
        title = ""
        subTitle = ""
        contentList=[]
        captions = []
        #links = []

        soup = BeautifulSoup(response.content, 'html.parser') 
        if soup.find('h1'):
            title = soup.find('h1')
        if soup.find('div', class_='dcr-4gwv1z'):
            subTitle = soup.find('div', class_='dcr-4gwv1z').get_text()
        if soup.find('span', class_="dcr-1qvd3m6"):
            for caption in soup.find_all('span', class_="dcr-1qvd3m6"):
                if caption.get_text() not in captions:
                    captions.append(caption.get_text())
        if soup.find_all('p', class_="dcr-s3ycb2"):
            for p in soup.find_all('p', class_="dcr-s3ycb2"):
                contentList.append(p.get_text() + "\n")
        else:       
           print("2nd")
           return getArticleData('18daef39-58e5-4824-a400-51efa5799e43', articleUrl)

        content = "".join(contentList)
        articleData = {
            #"title": title,
            "url": articleUrl,
            "subTitle": subTitle,
            "content": content,
            "captions": captions,
        }
        return articleData

# Example usage:
api_key = '18daef39-58e5-4824-a400-51efa5799e43'
#headlines = get_latest_headlines(api_key, num_results=10)
#article_data = getArticleData(api_key, "https://www.theguardian.com/lifeandstyle/2025/feb/25/my-truck-plunged-into-a-ravine-six-days-trapped-alone-afraid")
"""for item in headlines:
    print(item)"""
