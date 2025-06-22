import scrapy
import hashlib
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
import re


class KsuwebspiderSpider(CrawlSpider):
    name = "ksuWebSpider"
    # Define the allowed domains for the spider.
    allowed_domains = ["kennesaw.edu"]
    
    # Define the start URLs for the spider.
    start_urls = [
        "https://www.kennesaw.edu",
        "https://ccse.kennesaw.edu",
        "https://coles.kennesaw.edu"
    ]

    rules = (
        Rule(
            LinkExtractor(allow_domains=allowed_domains),
            callback='parse_item',  # CHANGED FROM 'parse' to 'parse_item'
            follow=True
        ),
    )

    def get_page_id(self, url):
        #Generate a unique page ID based on the URL.
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_page_title(self, response):
        #Extract the page title from the response.
        return response.xpath('//title/text()').get(default='No Title').strip()
    
    def get_page_body(self, response):
        #Extract the main content of the page.
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        return ''
    
    def extract_emails(self, text):
        #Extract email addresses from the text.
        return re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)

    # RENAMED from parse to parse_item
    def parse_item(self, response):
        url = response.url
        pageid = self.get_page_id(url)
        title = self.get_page_title(response)
        body = self.get_page_body(response)
        emails = self.extract_emails(body)

        entry = {
            'pageid': pageid,
            'url': url,
            'title': title,
            'body': body,
            'emails': emails
        }
        yield entry