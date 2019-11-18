# -*- coding: utf-8 -*-
import scrapy
import os.path
import json
import re
import js2xml
import lxml.etree
from parsel import Selector
from scrapy_splash import SplashRequest
from aliexpress.items import AliexpressItem
from scrapy.loader import ItemLoader
from urllib.parse import urlparse


class AliSpider(scrapy.Spider):
    http_user = 'user'
    http_pass = 'userpass'
    name = 'ali'


    headers =  {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
    }

    scripts = '''
    function main(splash, args)
  assert(splash:go(args.url))
  local btn_close = splash:select("a.next-dialog-close")
  if btn_close ~= null then
    btn_close:click()
  end
  assert(splash:wait(0.5))
  return splash:html()
end
    '''

    def build_api_call(self,productId):
        query = 'https://aeproductsourcesite.alicdn.com/product/description/pc/v2/en_US/desc.htm?productId={productId}&key=Hcbc493fe28fe4f9c8e30a7e15a708fb6t.zip&token=ac3a81eab0bc49ca97b34fd3ff03fa21&v=1'.format(productId=productId)
        print("Query = ", query)
        return query

    def start_requests(self):

        urls = [
            'https://www.aliexpress.com/item/32949546018.html',
            'https://www.aliexpress.com/item/4000259927411.html',
            'https://www.aliexpress.com/item/4000067965945.html',
            'https://www.aliexpress.com/item/32950477660.html',
            'https://www.aliexpress.com/item/4000154697607.html',
            'https://www.aliexpress.com/item/4000259927411.html',
            'https://www.aliexpress.com/item/32911451642.html',
            'https://www.aliexpress.com/item/4000065355325.html',
            'https://www.aliexpress.com/item/32999480456.html',
            'https://www.aliexpress.com/item/4000135076694.html',
            'https://www.aliexpress.com/item/4000064692319.html',
            'https://www.aliexpress.com/item/4000064867831.html',
            'https://www.aliexpress.com/item/32998465778.html',
           
        ]
        for url in urls:
           yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'wait':0.5,
                'lua_source': self.scripts,
                'proxy':'http://hohung:ho123456789@us-wa.proxymesh.com:31280'
            },
            dont_filter=True
        )

    def parse(self,response):
        product = AliexpressItem()
        product['Name'] = response.xpath("//div[@class='product-title']/text()").extract_first()
        product['Sale_price'] = response.xpath("//div[@class='product-price-current']//span[@class='product-price-value']/text()").extract_first()
        product['Regular_price'] = response.xpath("//div[@class='product-price-original']//span[@class='product-price-value']/text()").extract_first()
        product['image_urls'] = response.xpath("//ul[@class='images-view-list']//img/@src").extract()
        
        

        # data = json.dumps(response.xpath("//*[contains(text(),'window.runParams')]/text()").extract_first())
        # self.logger.info('data : %s', data)
        # json_data = json.loads(data)
        # descriptionUrl = json_data.get('data')[0].get('descriptionModule')[0].get('descriptionUrl')
        # self.logger.info('descriptionUrl : %s', descriptionUrl)

        # product['Link'] = link
        # a = urlparse(link)
        # productId = os.path.basename(a.path).split('.')[0]
        # self.logger.info('link : %s', a)
        # self.logger.info('productId : %s', productId)
        # callUrl = self.build_api_call(productId)

        # data = re.findall("window.runParams =(.+?);\n", response.body.decode("utf-8"), re.S)

        # json_data = []
        # if data:
        #     json_data = json.loads(data[0])
        #     self.logger.info('data : %s', json_data)

        # descriptionUrl = json_data.get('data')[0].get('descriptionModule')[0].get('descriptionUrl')
        # self.logger.info('descriptionUrl : %s', descriptionUrl)

        javascript = response.xpath("//*[contains(text(),'window.runParams')]/text()").extract_first()
        xml = lxml.etree.tostring(js2xml.parse(javascript), encoding='unicode')
        selector = Selector(text=xml)
        descriptionUrl = selector.xpath("//property[@name='descriptionUrl']/string/text()").get()
       

        yield SplashRequest(
            url=descriptionUrl,
            callback=self.parse_detail,
            endpoint='render.html',
            args={'wait':0.5,
                'proxy':'http://hohung:ho123456789@us-wa.proxymesh.com:31280'
            },
            meta={'product':product},
            dont_filter=True
        )

    def parse_detail(self,response):
        product = response.meta['product']
        description = response.xpath("//body/*[not(self::script)]").extract()
        loader = ItemLoader(item=AliexpressItem())
        self.logger.info(response)
        loader.add_value('Name', product['Name'])
        loader.add_value('Sale_price', product['Sale_price'])
        loader.add_value('Regular_price',product['Regular_price'])
        loader.add_value('image_urls',product['image_urls'])
        loader.add_value('Description',description)
       
        # loader.add_xpath('Weight',"//div[@class='description bottom']")
        # loader.add_xpath('Length',"//h1[@class='product_name']/text()")
        # loader.add_xpath('Width',"//div[@class='description bottom']")
        # loader.add_xpath('Height',"//h1[@class='product_name']/text()")
        # loader.add_xpath('Categories',"//div[@class='description bottom']")
        # loader.add_xpath('Number_Of_Reviews',"//h1[@class='product_name']/text()")
        yield loader.load_item()