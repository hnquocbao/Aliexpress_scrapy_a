# -*- coding: utf-8 -*-
import scrapy
import os.path
import json
import re
import js2xml
import lxml.etree
import pandas
from parsel import Selector
from scrapy_splash import SplashRequest
from aliexpress.items import AliexpressItem
from scrapy.loader import ItemLoader
from urllib.parse import urlparse
from urllib.parse import quote


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

        # excel_data_df = pandas.read_excel('do_go_ali.xlsx', sheet_name='Sheet1')

        # urls = excel_data_df['Link'].tolist()
        urls = ['https://www.aliexpress.com/item/32971101049.html']
        
        for url in urls:
           yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'wait':0.5,'lua_source':self.scripts}
            # 'proxy':'http://woodenbe9:W@@denBe#@us-wa.proxymesh.com:31280'
        )

    def parse(self,response):

        # crawl despition and get url
        javascript = response.xpath("//*[contains(text(),'window.runParams')]/text()").extract_first()
        xml = lxml.etree.tostring(js2xml.parse(javascript), encoding='unicode')
        selector = Selector(text=xml)
        descriptionUrl = selector.xpath("//property[@name='descriptionUrl']/string/text()").get()
        productId = selector.xpath("//property[@name='productId']/number/@value").get()

        priceMap_regular = {}
        priceMap_sale = {}
        
        skuPriceList = selector.xpath("//property[@name='skuPriceList']/array/object")
        for i in range(len(skuPriceList)):
            sku_name = ""
            text = skuPriceList.xpath("//property[@name='skuAttr']/string/text()")[i].get()
            text_0 = text.split("#")
            text_1 = text_0[1].split(";")
            sku_name = text_1[0]
            sku_regular_price = skuPriceList.xpath("//property[@name='skuVal']/object/property[@name='skuAmount']/object/property[@name='value']/number/@value")[i].get()
            sku_sale_price = skuPriceList.xpath("//property[@name='skuVal']/object/property[@name='skuActivityAmount']/object/property[@name='value']/number/@value")[i].get()
            priceMap_regular[sku_name] = sku_regular_price
            priceMap_sale[sku_name] = sku_sale_price



        Name = response.xpath("//div[@class='product-title']/text()").extract_first()
        Sale_price = response.xpath("//div[@class='product-price-current']//span[@class='product-price-value']/text()").extract_first()
        Regular_price = response.xpath("//div[@class='product-price-original']//span[@class='product-price-value']/text()").extract_first()
        image_urls = response.xpath("//ul[@class='images-view-list']//img/@src").extract()
        SKU = "Woodenbe_" + productId


        product = AliexpressItem()
        product['Name'] = Name if Name else ""
        product['Sale_price'] = Sale_price if Sale_price else ""
        self.logger.info("Regular_price: %s parse", Regular_price)
        product['Regular_price'] = Regular_price if Regular_price else ""
        product['image_urls'] = image_urls if image_urls else []
        product['Type'] = "variable"
        product['SKU'] = SKU

        
        product['attrs']  = response.xpath("//div[@class='sku-property']")
        product['priceMap_regular']  = priceMap_regular
        product['priceMap_sale']  = priceMap_sale

        yield SplashRequest(
            url=descriptionUrl,
            callback=self.parse_detail,
            endpoint='render.html',
            meta={'product':product},
            dont_filter=True
        )

    def parse_detail(self,response):
        products = []

        p_product = response.meta['product']
        attrs = p_product['attrs']
        priceMap_sale = p_product['priceMap_sale']
        priceMap_regular = p_product['priceMap_regular']

      
        description = response.xpath("//body").extract_first()

        loader_p = ItemLoader(item=AliexpressItem(),selector=attrs)
        loader_p.add_value('SKU', p_product['SKU'])
        loader_p.add_value('Name', p_product['Name'])
        loader_p.add_value('Sale_price', p_product['Sale_price'])
        loader_p.add_value('Regular_price',p_product['Regular_price'])
        loader_p.add_value('image_urls',p_product['image_urls'])
        loader_p.add_value('Description',description)

                    
        Attribute_1_name = attrs.xpath("//div[@class='sku-property'][1]/div[@class='sku-title']/text()").extract_first()
        loader_p.add_xpath('Attribute_1_name', "//div[@class='sku-property'][1]/div[@class='sku-title']/text()")
        img_values_1 = set(attrs.xpath("//div[@class='sku-property'][1]/ul[@class='sku-property-list']/li/div/img/@title").extract())
        string_values_1 = set(attrs.xpath("//div[@class='sku-property'][1]/ul/li/div/span/text()").extract())
        if img_values_1 :
            loader_p.add_value('Attribute_1_values',img_values_1)
        elif string_values_1:
            loader_p.add_value('Attribute_1_values',string_values_1)


        Attribute_2_name = attrs.xpath("//div[@class='sku-property'][2]/div[@class='sku-title']/text()").extract_first()
        loader_p.add_xpath('Attribute_2_name', "//div[@class='sku-property'][2]/div[@class='sku-title']/text()")
        img_values_2 = set(attrs.xpath("//div[@class='sku-property'][2]/ul[@class='sku-property-list']/li/div/img/@title").extract())
        string_values_2 = set(attrs.xpath("//div[@class='sku-property'][2]/ul/li/div/span/text()").extract())
        Attribute_2_values = []
        if img_values_2 :
            loader_p.add_value('Attribute_2_values',img_values_2)
            Attribute_2_values = img_values_2
        elif string_values_2:
            loader_p.add_value('Attribute_2_values',string_values_2)
            Attribute_2_values = string_values_2

        Attribute_3_name = attrs.xpath("//div[@class='sku-property'][3]/div[@class='sku-title']/text()").extract_first()
        loader_p.add_xpath('Attribute_3_name', "//div[@class='sku-property'][3]/div[@class='sku-title']/text()")
        img_values_3 = set(attrs.xpath("//div[@class='sku-property'][3]/ul[@class='sku-property-list']/li/div/img/@title").extract())
        Attribute_3_values = []
        string_values_3 = set(attrs.xpath("//div[@class='sku-property'][3]/ul/li/div/span/text()").extract())
        if img_values_3 :
            loader_p.add_value('Attribute_3_values',img_values_3)
            Attribute_3_values = img_values_3
        elif string_values_3:
            loader_p.add_value('Attribute_3_values',string_values_3)
            Attribute_3_values = string_values_3
        

        if img_values_1 or string_values_1 or img_values_2 or string_values_2 or img_values_3 or string_values_3 :
            loader_p.add_value('Type', 'variable')
        elif len(img_values_1) <= 1: 
            loader_p.add_value('Type', 'simple')

        products.append(loader_p.load_item())


        img_names = set(attrs.xpath("//div[@class='sku-property'][1]/ul/li[@class='sku-property-item']/div/img/@title").extract())
        img_links = set(attrs.xpath("//div[@class='sku-property'][1]/ul/li[@class='sku-property-item']/div/img/@src").extract())
        string_values = set(attrs.xpath("//div[@class='sku-property'][1]/ul/li[@class='sku-property-item']/div/span/text()").extract())
        
        attr_names = []
        attr_values = []
        if img_names and img_links:
            attr_names = img_names
            attr_values = img_links
        elif string_values:
            attr_names = string_values

        for index,attr_name in enumerate(attr_names,start=0):

            loader = ItemLoader(item=AliexpressItem(),selector=attrs)
            loader.add_value('SKU',p_product['SKU'] + "-" + attr_name)
            loader.add_value('Name', p_product['Name'] + "-" + attr_name)
            loader.add_value('Sale_price', priceMap_sale[attr_name])
            loader.add_value('Regular_price', priceMap_regular[attr_name] )
            loader.add_value('image_urls',list(attr_values)[index])
            loader.add_value('Description',"")
            loader.add_value('Type','variation')
            loader.add_value('Attribute_1_name', Attribute_1_name if Attribute_1_name else "")
            loader.add_value('Attribute_1_values',attr_name)
            
            if Attribute_2_name and Attribute_2_values:
                loader.add_value('Attribute_2_name', Attribute_2_name if Attribute_2_name else "")
                loader.add_value('Attribute_2_values',list(Attribute_2_values)[0]) #get 1st value of attribute 2
            else:
                loader.add_value('Attribute_2_name', "")
                loader.add_value('Attribute_2_values',[]) #get 1st value of attribute 2
            
            if Attribute_3_name and Attribute_3_values:
                loader.add_value('Attribute_3_name', Attribute_3_name if Attribute_3_name else "")
                loader.add_value('Attribute_3_values',list(Attribute_3_values)[0]) #get 1st value of attribute 2
            else:
                loader.add_value('Attribute_3_name', "")
                loader.add_value('Attribute_3_values',[]) #get 1st value of attribute 3
            
            
            products.append(loader.load_item())

        for product in products:
            
            attribute_2_name = ""
            attribute_2_values = []
            attribute_3_name = ""
            attribute_3_values = []
            try:
                attribute_2_name = product['Attribute_2_name']
            except:
                attribute_2_name = ""
            try:
                attribute_3_name = product['Attribute_3_name']
            except:
                attribute_3_name = ""
            try:
                attribute_2_values = product['Attribute_2_values']
            except:
                attribute_2_values = []
            try:
                attribute_3_values = product['Attribute_3_values']
            except:
                attribute_3_values = []

            yield {
                'ID': "",
                'Type': product['Type'],
                'SKU': product['SKU'],
                'Name': product['Name'],
                'Published': "0",
                'Is featured?': "1",
                'Visibility in catalog': "visible",
                'Short description': "",
                'Description': product['Description'],
                'Date sale price starts': "",
                'Date sale price ends': "",
                'Tax status': "taxable",
                'Tax class': "",
                'In stock?': "1",
                'Stock': "",
                'Backorders allowed?': "0",
                'Sold individually?': "0",
                'Weight (lbs)': "",
                'Length (in)': "",
                'Width (in)': "",
                'Height (in)': "",
                'Allow customer reviews?': "1",
                'Purchase note': "",
                'Sale price': product['Sale_price'],
                'Regular price': product['Regular_price'],
                'Categories': "",
                'Tags': "",
                'Shipping class': "",
                'Images': product['image_urls'],
                'Download limit': "",
                'Download expiry days': "",
                'Parent': "",
                'Grouped products': "",
                'Upsells': "",
                'Cross-sells': "",
                'External URL': "",
                'Button text': "",
                'Position': "0",
                'Attribute 1 name': product['Attribute_1_name'],
                'Attribute 1 value(s)':  product['Attribute_1_values'],
                'Attribute 1 visible': "1",
                'Attribute 1 global': "1",
                'Attribute 2 name': attribute_2_name,
                'Attribute 2 value(s)': attribute_2_values,
                'Attribute 2 visible': "1",
                'Attribute 2 global': "1",
                'Attribute 3 name': attribute_3_name,
                'Attribute 3 value(s)': attribute_3_values,
                'Attribute 3 visible': "1",
                'Attribute 3 global': "1",
                'Meta: _wpcom_is_markdown': "1",
                'Download 1 name': "",
                'Download 1 URL': "",
                'Download 2 name': "",
                'Download 2 URL': "",
            }