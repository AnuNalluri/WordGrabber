import scrapy
import os

import sqlite3
from sqlite3 import Error

from article import Article

db = os.environ["VISITED_URLS"]
tablename = "VISITED_URLS"
col1 = "URLS"
field_type = 'TEXT'

class FakeNewsSpider(scrapy.Spider):

	name = "FNAB"

	# initial method run by scrapy
	def start_requests(self):
		try:
			conn = sqlite3.connect(db)
			c = conn.cursor()
			c.execute('CREATE TABLE {tn} ({nf} {ft})'\
				.format(tn = tablename, nf = col1, ft = field_type))
		except Error as e:
			
			print(e)
			conn.close()
		urls = tuple(open(os.environ["URL_LIST"], 'r'))
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	# call back for each web page
	def parse(self, response):

		# data model for parsing
		data = Article(response)

		try:
			conn = sqlite3.connect(db)
			c = conn.cursor()
			c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf} {ft})'\
				.format(tn = tablename, nf = col1, ft = field_type))
		except Error as e:
			
			print(e)
			conn.close()
		
		# saves data of article to a file, we should move to a database after
		data.save_to_file(data.url)

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


