# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import os.path
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags
from urllib.parse import urlparse


def remove_utext(value):
   return value.replace(u"\u1ed9",'').replace(u"\u1eef",'').replace(u"\u00e1",'').replace(u"\u20ab",'').replace(u"\u1ed6",'').replace(u"\u00A0",'')

def remove_currencySymbol(value):
    return value.replace("US",'').replace("$",'')

def slit_image_url(value):
    return value.replace("_50x50.jpg",'')

def convertToString(encodedString):
     return encodedString.encode("utf-8").decode('unicode_escape').encode('ascii', 'ignore')


class AliexpressItem(scrapy.Item):
    Name = scrapy.Field(
        input_processor= MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    Description = scrapy.Field(
        input_processor= MapCompose(remove_tags,remove_utext,str.strip),
    )
    Short_description = scrapy.Field(
        input_processor= MapCompose(remove_tags,remove_utext,str.strip),
    )
    
    Sale_price  = scrapy.Field(
        input_processor= MapCompose(remove_currencySymbol,str.strip),
        output_processor = TakeFirst()
    )
    Regular_price  = scrapy.Field(
        input_processor= MapCompose(remove_currencySymbol,str.strip),
        output_processor = TakeFirst()
    )

    Link = scrapy.Field()

    image_urls = scrapy.Field(
        input_processor= MapCompose(slit_image_url)
    )
    images = scrapy.Field()
