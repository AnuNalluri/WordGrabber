import scrapy
import os
from article import Article

class FakeNewsSpider(scrapy.Spider):

    name = "FNAB"

    # initial method run by scrapy
    def start_requests(self):
        urls = tuple(open(os.environ["URL_LIST"], 'r'))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # call back for each web page
    def parse(self, response):
        # data model for parsing
        data = Article(response)

        # saves data of article to a file, we should move to a database after
        data.save_to_file(data.url)

        # iterate through the links on the page and continue crawling
        for link in data.get_links():
            yield response.follow(link, callback=self.parse)


