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

def remove_sysbols(value):
    return value.replace("US",'').replace("$",'').replace(":",'')

def slit_image_url(value):
    return value.replace("_50x50.jpg",'')


class AliexpressItem(scrapy.Item):
    # ID = scrapy.Field()
    # SKU = scrapy.Field()
    # Published = scrapy.Field()
    # Is_featured = scrapy.Field()
    # Visibility_in_catalog = scrapy.Field()
    # Date_sale_price_starts = scrapy.Field()
    # Date_sale_price_ends = scrapy.Field()
    # Tax_status = scrapy.Field()
    # Tax_class = scrapy.Field()
    # ID = scrapy.Field()
    # Type = scrapy.Field()
    # Published = scrapy.Field()
    # Is_featured = scrapy.Field()
    # Visibility_in_catalog = scrapy.Field()
    # Date_sale_price_starts = scrapy.Field()
    # Date_sale_price_ends = scrapy.Field()
    # Tax_status = scrapy.Field()
    # Tax_class = scrapy.Field()
    # In_stock = scrapy.Field()
    
    # Backorders_allowed = scrapy.Field()
    # Sold_individually = scrapy.Field()
    # Weight = scrapy.Field()
    # Length = scrapy.Field()
    # Width = scrapy.Field()
    # Height = scrapy.Field()
    # Allow_customer_reviews = scrapy.Field()
    # Categories = scrapy.Field()
    # Tags = scrapy.Field()
    # Shipping_class = scrapy.Field()
    # Download_limit = scrapy.Field()
    # Download_expiry_days = scrapy.Field()
   
    # Grouped_products = scrapy.Field()
    # Upsells = scrapy.Field()
    # Cross_sells = scrapy.Field()
    # External_URL = scrapy.Field()
    # Button_text = scrapy.Field()
    # Position = scrapy.Field()
    # Meta_wpcom_is_markdown = scrapy.Field()
    # Download_1_name = scrapy.Field()
    # Download_1_URL = scrapy.Field()
    # Download_1_name = scrapy.Field()
    # Download_2_URL = scrapy.Field()

    Type = scrapy.Field()
    SKU = scrapy.Field()
    Parent = scrapy.Field()
    Stock = scrapy.Field()

    productSKUPropertyList = scrapy.Field()
    skuPriceList = scrapy.Field()



    Attribute_1_name = scrapy.Field(
        input_processor= MapCompose(remove_sysbols)
    )
    Attribute_1_values = scrapy.Field()
    Attribute_1_visible =  scrapy.Field()
    Attribute_1_global =  scrapy.Field()
    Attribute_1_img_link =  scrapy.Field(
        input_processor= MapCompose(slit_image_url)
    )


    Attribute_2_name = scrapy.Field(
         input_processor= MapCompose(remove_sysbols)
    )
    Attribute_2_values = scrapy.Field()
    Attribute_2_visible =  scrapy.Field()
    Attribute_2_global =  scrapy.Field()
    Attribute_2_img_link =  scrapy.Field(
        input_processor= MapCompose(slit_image_url)
    )

    Attribute_3_name = scrapy.Field(
         input_processor= MapCompose(remove_sysbols)
    )
    Attribute_3_values = scrapy.Field()
    Attribute_3_visible =  scrapy.Field()
    Attribute_3_global =  scrapy.Field()
    Attribute_3_img_link =  scrapy.Field(
        input_processor= MapCompose(slit_image_url)
    )

   
    
    Name = scrapy.Field(
        input_processor= MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    Description = scrapy.Field(
        # input_processor= MapCompose(remove_tags,remove_utext,str.strip),
    )
    Short_description = scrapy.Field(
        input_processor= MapCompose(remove_tags,remove_utext,str.strip),
    )
    
    Sale_price  = scrapy.Field(
        input_processor= MapCompose(remove_sysbols,str.strip)
    )
    Regular_price  = scrapy.Field(
        input_processor= MapCompose(remove_sysbols,str.strip)
    )

    Link = scrapy.Field()

    image_urls = scrapy.Field(
        input_processor= MapCompose(slit_image_url)
    )
    images = scrapy.Field()
