# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AlbumItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    releaseId = scrapy.Field()
    have = scrapy.Field()
    want = scrapy.Field()
    price = scrapy.Field()
    style = scrapy.Field()

