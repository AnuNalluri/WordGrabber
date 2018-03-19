import scrapy
import os
import sqlite3
from sqlite3 import Error

from article import Article

class FakeNewsSpider(scrapy.Spider):

    name = "FNAB"
    CONCURRENT_REQUESTS = 100
    REACTOR_THREADPOOL_MAXSIZE = 20
    tablename = "VISITED_URLS"
    col1 = "URLS"
    field_type = 'TEXT'
    db = os.environ["VISITED_URLS"]
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf} {ft})'\
              .format(tn = tablename, nf = col1, ft = field_type))
    
    # initial method run by scrapy
    def start_requests(self):
        urls = tuple(open(os.environ["URL_LIST"], 'r'))
        for url in urls:
	    url = url.rstrip()
            yield scrapy.Request(url=url, callback=self.parse)

    # call back for each web page
    def parse(self, response):
        # data model for parsing
        data = Article(response)

		# iterate through the links on the page and continue crawling
		for link in data.get_links():
			# check to see if url exists in sqllite db
			row = c.execute("SELECT * FROM " + tablename + " WHERE " + col1 + " = ?", (link,))

			# if it does then do not yield, if it doesn't then add it to db and yield
			if row.fetchone() == None:

				c.execute("INSERT INTO " + tablename + " (" + col1 + ") VALUES (?)", (link,))
				conn.commit()
				yield response.follow(link, callback=self.parse)

		conn.close()

