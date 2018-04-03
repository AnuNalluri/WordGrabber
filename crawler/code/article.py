import os
import json
import tldextract
try:
	from urllib.parse import urlparse
except ImportError:
	 from urlparse import urlparse


class Page:

	def __init__(self, response):
		self.hostname = tldextract.extract(response.url).domain #urlparse(response.url).hostname
		self.url = response.url
		self.html = response.text
		self.hostlinks = [tldextract.extract(link.extract()).domain for link in response.xpath("//a/@href")]

		self.hostname = self.hostname.replace(",", "")
		self.hostname = self.hostname.replace(" ", "")

	def save_to_file(self):
		with open(os.environ["DATA_DIR"] + self.hostname, "a+") as f:
			to_write = {"URL": self.url, "HTML": self.html, "outlinks": self.hostlinks}
			f.write(json.dumps(to_write, separators = (',', ': ')) + "\n~~~~~~\n");

class Article:

	def __init__(self, response, lazy=False):
		self.response = response
		if not lazy:
			self.extract_data()

	def extract_data(self):
		self.title = self.response.xpath("//title/text()").extract()
		self.links = [link.extract() for link in self.response.xpath("//a/@href")]
		self.url = tldextract.extract(self.response.url).domain
		# include other data types that we are looking for

	def to_dict(self):
		return self.__dict__
	def save_to_file(self):
		new_page =  Page(self.response)
		new_page.save_to_file()

	def get_title(self):
		return self.title

	def get_links(self):
		return self.links 

	def get_url(self):
		return self.url
