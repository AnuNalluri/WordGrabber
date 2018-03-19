import os
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

class Article:

    def __init__(self, response, lazy=False):
        self.response = response
        if not lazy:
            self.extract_data()

    def extract_data(self):
        self.title = self.response.xpath("//title/text()").extract()
        self.links = [link.extract() for link in self.response.xpath("//a/@href")]
        self.url = urlparse(self.response.url).hostname
        # include other data types that we are looking for

    def to_dict(self):
        return self.__dict__

    def save_to_file(self, filename):
        with open(os.environ["DATA_DIR"] + filename, "a+") as f:
            f.write(str(self.to_dict()))

    def get_title(self):
        return self.title

    def get_links(self):
        return self.links 

    def get_url(self):
        return self.url
