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
  assert(splash:wait(3))
  return splash:html()
end
    '''

    def build_api_call(self,productId):
        query = 'https://aeproductsourcesite.alicdn.com/product/description/pc/v2/en_US/desc.htm?productId={productId}&key=Hcbc493fe28fe4f9c8e30a7e15a708fb6t.zip&token=ac3a81eab0bc49ca97b34fd3ff03fa21&v=1'.format(productId=productId)
        print("Query = ", query)
        return query

    def start_requests(self):

        # urls = [
        #     'https://www.aliexpress.com/item/32918112210.html',
        #     'https://www.aliexpress.com/item/32971101049.html',
        #     'https://www.aliexpress.com/item/32849564667.html',
        # ]

        excel_data_df = pandas.read_excel('danh_sach_cac_sp_go.xls', sheet_name='Sheet1')
        urls = excel_data_df['Link'].tolist()
        
        for url in urls:
           yield SplashRequest(
            url=url,
            callback=self.parse,
            endpoint='execute',
            args={'wait':3,'lua_source':self.scripts,'proxy':'http://thaohappy:1234567@us-wa.proxymesh.com:31280'},
            dont_filter=True
        )

    def parse(self,response):

        # crawl despition and get url
        # javascript = response.xpath("//*[contains(text(),'window.runParams')]/text()").extract_first()
        # xml = lxml.etree.tostring(js2xml.parse(javascript), encoding='unicode')
        # selector = Selector(text=xml)
        # descriptionUrl = selector.xpath("//property[@name='descriptionUrl']/string/text()").get()
        # productId = selector.xpath("//property[@name='productId']/number/@value").get()


        data = re.findall("data:(.+?),\n", response.body.decode("utf-8"), re.S)
        json_data = json.loads(data[0])

        descriptionUrl = json_data.get('descriptionModule').get('descriptionUrl')
        productId = json_data.get('descriptionModule').get('productId')

        productSKUPropertyList = json_data.get('skuModule').get('productSKUPropertyList')
        skuPriceList = json_data.get('skuModule').get('skuPriceList')
 

        Name = response.xpath("//div[@class='product-title']/text()").extract_first()
        image_urls = response.xpath("//ul[@class='images-view-list']//img/@src").extract()
        SKU = "Woodenbe_" + str(productId)


        try:
            Sale_price = json_data.get('priceModule').get('formatedActivityPrice')
        except :
            Sale_price = ""
        Regular_price = json_data.get('priceModule').get('formatedPrice')


        product = AliexpressItem()
        product['Name'] = Name if Name else ""
        product['Sale_price'] = Sale_price if Sale_price else ""
        self.logger.info("Regular_price: %s parse", Regular_price)
        product['Regular_price'] = Regular_price if Regular_price else ""
        product['image_urls'] = image_urls if image_urls else []
        product['SKU'] = SKU

        
        product['productSKUPropertyList']  = productSKUPropertyList
        product['skuPriceList']  = skuPriceList


        yield SplashRequest(
            url=descriptionUrl,
            callback=self.parse_detail,
            endpoint='render.html',
            args={'wait':2,'proxy':'http://thaohappy:1234567@us-wa.proxymesh.com:31280'},
            meta={'product':product},
            dont_filter=True
        )

    def parse_detail(self,response):
        products = []
        p_product = response.meta['product']

        productSKUPropertyList = p_product['productSKUPropertyList']
        skuPriceList = p_product['skuPriceList']

        description = response.xpath("//body").extract_first()

        loader_p = ItemLoader(item=AliexpressItem())
        loader_p.add_value('SKU', p_product['SKU'])
        loader_p.add_value('Name', p_product['Name'])
        loader_p.add_value('Sale_price', p_product['Sale_price'])
        loader_p.add_value('Regular_price',p_product['Regular_price'])
        loader_p.add_value('image_urls',p_product['image_urls'])
        loader_p.add_value('Description',description)

        SKUPropertyNames = {}
        SKUPropertyValues = {}
        SKUPropertyImgLinks = {}
        Attribute_1_values = []
        Attribute_2_values = []
        Attribute_3_values = []
        

        for Property in productSKUPropertyList:
            SKUPropertyNames[Property.get('skuPropertyId')] = Property.get('skuPropertyName')
            for value in Property.get('skuPropertyValues'):
                SKUPropertyValues[value.get('propertyValueId')] = value.get('propertyValueDisplayName')
                SKUPropertyImgLinks[value.get('propertyValueId')] = value.get('skuPropertyImagePath')

        if productSKUPropertyList:
            for item in productSKUPropertyList[0].get('skuPropertyValues'):
                Attribute_1_values.append(item.get('propertyValueDisplayName'))
                
            Attribute_1_name = productSKUPropertyList[0].get('skuPropertyName')
            loader_p.add_value('Type', 'variable')
            loader_p.add_value('Attribute_1_name', Attribute_1_name)
            loader_p.add_value('Attribute_1_values',Attribute_1_values)
            ParentSKU = p_product['SKU']
        else:
            loader_p.add_value('Type', 'simple')
            ParentSKU = ""

        if len(productSKUPropertyList) >= 2:
            for item in productSKUPropertyList[1].get('skuPropertyValues'):
                Attribute_2_values.append(item.get('propertyValueDisplayName'))
                
            Attribute_2_name = productSKUPropertyList[1].get('skuPropertyName')
            loader_p.add_value('Attribute_2_name', Attribute_2_name)
            loader_p.add_value('Attribute_2_values',Attribute_2_values)

        if len(productSKUPropertyList) >= 3:
            for item in productSKUPropertyList[2].get('skuPropertyValues'):
                Attribute_3_values.append(item.get('propertyValueDisplayName'))
            
            Attribute_3_name = productSKUPropertyList[2].get('skuPropertyName')
            loader_p.add_value('Attribute_3_name', Attribute_3_name)
            loader_p.add_value('Attribute_3_values',Attribute_3_values)

        products.append(loader_p.load_item())


        for skuItem in skuPriceList:
            skuAttr = skuItem.get('skuAttr')
            attrs = skuAttr.split(";")

            attrs_1 = []
            attrs_2 = []
            attrs_3 = []

            attrs_1 = attrs[0].split(":")
            attr_1_name = SKUPropertyNames[int(attrs_1[0])]
            attr_1_value = ""
            if "#" in attrs_1[1]:
                temp = attrs_1[1].split("#")
                attr_1_value_id = temp[0]
                attr_1_value = SKUPropertyValues[int(attr_1_value_id)]
            else:
                attr_1_value = SKUPropertyValues[int(attrs_1[1])]
                attr_1_value_id = int(attrs_1[1])
            
            attr_2_name = ""
            attr_2_value = ""
            if len(attrs) >=2 :
                attrs_2 = attrs[1].split(":")
                attr_2_name = SKUPropertyNames[int(attrs_2[0])]
                if "#" in attrs_2[1]:
                    temp = attrs_2[1].split("#")
                    attr_2_value = SKUPropertyValues[int(temp[0])]
                else:
                    attr_2_value = SKUPropertyValues[int(attrs_2[1])]

            attr_3_name = ""
            attr_3_value = ""
            if len(attrs) >= 3 :
                attrs_3 = attrs[2].split(":")
                attr_3_name = SKUPropertyNames[int(attrs_3[0])]
                if "#" in attrs_3[1]:
                    temp = attrs_3[1].split("#")
                    attr_3_value = SKUPropertyValues[int(temp[0])]
                else:
                    attr_3_value = SKUPropertyValues[int(attrs_3[1])]

            try:
                salePrice = skuItem.get('skuVal').get('skuActivityAmount').get('value')
            except :
                salePrice = ""

            try:
                img_paths = SKUPropertyImgLinks[int(attr_1_value_id)]
            except :
                img_paths = ""

            try:
                stock = skuItem.get('skuVal').get('availQuantity')
            except:
                stock = ""

            regularPrice = skuItem.get('skuVal').get('skuAmount').get('value')
            

            loader = ItemLoader(item=AliexpressItem())
            loader.add_value('SKU',"W" + "-" + str(skuItem.get('skuId')))
            loader.add_value('Name', p_product['Name'] + "-" + attr_1_value)
            loader.add_value('Parent', ParentSKU)

            loader.add_value('Sale_price', str(salePrice) if salePrice else "")
            loader.add_value('Regular_price', str(regularPrice))
            loader.add_value('Stock', str(stock))
            loader.add_value('image_urls',img_paths)
            loader.add_value('Description',"")
            loader.add_value('Type','variation')
            loader.add_value('Attribute_1_name', attr_1_name)
            loader.add_value('Attribute_1_values',attr_1_value)
            
            loader.add_value('Attribute_2_name', attr_2_name)
            loader.add_value('Attribute_2_values',attr_2_value)
            
            loader.add_value('Attribute_3_name', attr_3_name)
            loader.add_value('Attribute_3_values',attr_3_value)
            
            
            products.append(loader.load_item())

        for product in products:
            try:
                parent = product['Parent']
            except:
                parent = ""
            try:
                stock = product['Stock']
            except:
                stock = ""
            try:
                sale_price = product['Sale_price'] 
            except:
                sale_price = ""
            try:
                img_urls = product['image_urls']
            except:
                img_urls = ""

            try:
                attr_name_2 = product["Attribute_2_name"]
                attr_value_2 = product["Attribute_2_values"]
                attr_visible_2 = "1"
                attr_global_2 = "1"
            except :
                attr_name_2 = ""
                attr_value_2 = ""
                attr_visible_2 = ""
                attr_global_2 = ""
            try:
                attr_name_3 = product["Attribute_3_name"]
                attr_value_3 = product["Attribute_3_values"]
                attr_visible_3 = "1"
                attr_global_3 = "1"
            except :
                attr_name_3 = ""
                attr_value_3 = ""
                attr_visible_3 = ""
                attr_global_3 = ""
            
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
                'Stock': stock,
                'Backorders allowed?': "1",
                'Sold individually?': "1",
                'Weight (lbs)': "",
                'Length (in)': "",
                'Width (in)': "",
                'Height (in)': "",
                'Allow customer reviews?': "1",
                'Purchase note': "",
                'Sale price': sale_price,
                'Regular price': product['Regular_price'],
                'Categories': "",
                'Tags': "",
                'Shipping class': "",
                'Images': img_urls,
                'Download limit': "",
                'Download expiry days': "",
                'Parent': parent,
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
                'Attribute 2 name': attr_name_2,
                'Attribute 2 value(s)': attr_value_2,
                'Attribute 2 visible': attr_visible_2,
                'Attribute 2 global': attr_global_2,
                'Attribute 3 name': attr_name_3,
                'Attribute 3 value(s)': attr_value_3,
                'Attribute 3 visible': attr_visible_3,
                'Attribute 3 global': attr_global_3,
                'Meta: _wpcom_is_markdown': "1",
                'Download 1 name': "",
                'Download 1 URL': "",
                'Download 2 name': "",
                'Download 2 URL': "",
            }