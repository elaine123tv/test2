from abc import ABC, abstractmethod

class WebScraper(ABC):
    @abstractmethod
    def getTopHeadlines(self, url):
        pass

    @abstractmethod
    def getArticleData(self, url):
        pass
