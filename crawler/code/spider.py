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

	#db = os.environ["VISITED_URLS"]
	#tablename = "VISITED_URLS"
	#col1 = "URLS"
	#field_type = 'TEXT'

	#try:
	#	conn = sqlite3.connect(db)
	#	c = conn.cursor()
	#	
	#	c.execute('CREATE TABLE {tn} ({nf} {ft})'\
	#		.format(tn = tablename, nf = col1, ft = field_type))


	#except Error as e:
	#	print(e)
	#	conn.close()

        # saves data of article to a file, we should move to a database after
              
        
        data.save_to_file(data.url)

        # iterate through the links on the page and continue crawling
        for link in data.get_links():
            # check to see if url exists in sqllite db, if it does then do not yield, if it doesn't then add it to db and yield 
            temp = FakeNewsSpider.c.execute(("SELECT COUNT({cn}) FROM {tn} WHERE {cn}=?").format(tn = FakeNewsSpider.tablename, cn = FakeNewsSpider.col1), (link,))
            val = temp.fetchall()
            if val[0][0] != 0:
		continue
	    FakeNewsSpider.c.execute(("INSERT INTO {} VALUES (?)").format(FakeNewsSpider.tablename), (link,))
            yield response.follow(link, callback=self.parse)
	FakeNewsSpider.conn.commit()


