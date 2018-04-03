import scrapy
import os
import sqlite3
from sqlite3 import Error

from article import Article
try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

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
	DEPTH_PRIORITY = 1
	SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
	SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
	custom_settings = {
		"SCHEDULER_DISK_QUEUE" : SCHEDULER_DISK_QUEUE,
		"DEPTH_PRIORITY" : 1,
		"SCHEDULER_MEMORY_QUEUE" : SCHEDULER_MEMORY_QUEUE,
	}
	# white_list = {"www.infowars.com", "www.naturalnews.com", "www.rt.com"} 

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
		data.save_to_file()
		# iterate through the links on the page and continue crawling
		gen = (link for link in data.get_links())
		for link in gen:
			# check to see if url exists in sqllite db
			row = FakeNewsSpider.c.execute("SELECT * FROM " + FakeNewsSpider.tablename + " WHERE " + FakeNewsSpider.col1 + " = ?", (link,))
			# if it does then do not yield, if it doesn't then add it to db and yield
			if row.fetchone() == None:
				FakeNewsSpider.c.execute("INSERT INTO " + FakeNewsSpider.tablename + " (" + FakeNewsSpider.col1 + ") VALUES (?)", (link,))
				FakeNewsSpider.conn.commit()
				yield response.follow(link, callback=self.parse)

		FakeNewsSpider.conn.commit()

