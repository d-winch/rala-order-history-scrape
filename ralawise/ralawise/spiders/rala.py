import os
import re

import scrapy
from dotenv import load_dotenv
from scrapy.http import Request

from ..items import RalawiseItem

load_dotenv()


class ScrapySpider(scrapy.Spider):
    name = 'rala'
    allowed_domains = ['https://shop.ralawise.com',
                       'shop.ralawise.com']
    start_urls = ['https://shop.ralawise.com']
 
    def parse(self, response):
        inputs = response.css('form input')
 
        formdata = {}
        for input in inputs:
            name = input.css('::attr(name)').get()
            value = input.css('::attr(value)').get()
            formdata[name] = value
        
        formdata['EmailAddress'] = os.getenv('EMAIL')
        formdata['Password'] = os.getenv('PASSWORD')
 
        del formdata[None]
        
        return scrapy.FormRequest.from_response(
            response,
            url = 'https://shop.ralawise.com/Services/Authentication/SignIn',
            formdata = formdata,
            formxpath = '//*[@id="loginFormDropdown"]/div/div/div/form',
            callback = self.parse_after_login
        )
 
    def parse_after_login(self, response):
        yield scrapy.Request('https://shop.ralawise.com/my-account/order-history/order-history/', callback=self.get_orders)
    
    def get_orders(self, response):
        orders_string = response.css(".orderHistoryBlock script").get()
        #orders = re.sub(r'.*window\.orderHistoryDataTable=', '', orders_string)
        orders = re.findall(r'https:\/\/shop\.ralawise\.com\/my-account\/order-history\/order-detail-page\/\?webOrderReference=\d*', orders_string)
        for url in orders:
            yield Request(url, callback=self.parse_order)
        
    def parse_order(self, response):
        order_id = response.xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/section/div[1]/div/div[1]/h2/span/text()').extract()[0]
        web_ref = response.xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/section/div[2]/div/div[2]/h2/span/text()').extract()[0]
        order_date = response.xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/section/div[1]/div/div[3]/h2/span/text()').extract()[0]
        order_total = response.xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/section/div[2]/div/div[4]/h2/span/text()').extract()[0]
        
        products = response.css('.card-body .order-summary-item')
        for p in products:
            product_code = p.css('.product-productcode::attr(value)').get()
            product_colour = p.css('.product-productcolour::attr(value)').get()
            product_size = p.css('.product-productsize::attr(value)').get()
            product_sku = p.css('.product-variantcode::attr(value)').get()
            order_qty = p.css('.product-orderqty::attr(value)').get()
            order_line = p.css('.product-orderline::attr(value)').get().strip()
            unit_price = p.css('.product-unitprice::attr(value)').get()
            
            ralawise_item = RalawiseItem()
            ralawise_item['product_code'] = product_code
            ralawise_item['product_colour'] = product_colour
            ralawise_item['product_size'] = product_size
            ralawise_item['product_sku'] = product_sku
            ralawise_item['order_qty'] = order_qty
            ralawise_item['order_line'] = order_line
            ralawise_item['unit_price'] = unit_price
            ralawise_item['order_id'] = order_id
            ralawise_item['web_ref'] = web_ref
            ralawise_item['order_date'] = order_date
            ralawise_item['order_total'] = order_total
            
            yield ralawise_item
