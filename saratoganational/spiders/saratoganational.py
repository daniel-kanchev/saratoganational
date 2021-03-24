import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from saratoganational.items import Article
import re


class SaratoganationalSpider(scrapy.Spider):
    name = 'saratoganational'
    start_urls = ['https://www.saratoganational.com/About/In-The-News']

    def parse(self, response):
        links = response.xpath('//a[@class="edn_readMore edn_readMoreButton"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="page"]/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//article//p//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        result = re.search('\((.*)\)', content)
        date = result.group(1)

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
