# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RalawiseItem(scrapy.Item):
    product_code = scrapy.Field()
    product_colour = scrapy.Field()
    product_size = scrapy.Field()
    product_sku = scrapy.Field()
    order_qty = scrapy.Field()
    order_line = scrapy.Field()
    unit_price = scrapy.Field()
    order_id = scrapy.Field()
    web_ref = scrapy.Field()
    order_date = scrapy.Field()
    order_total = scrapy.Field()
