# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline

class AliexpressPipeline(ImagesPipeline):
    def file_path(self, request, response, info):
        return 'files/' + os.path.basename(urlparse(request.url).path)
