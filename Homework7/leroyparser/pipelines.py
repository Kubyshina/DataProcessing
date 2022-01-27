# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pprint import pprint
from scrapy.pipelines.images import ImagesPipeline
import re
import hashlib
from scrapy.utils.python import to_bytes


class LeroyparserPipeline:
    def process_item(self, item, spider):
        item['price'] = self.process_price(item['price'])
        return item

    def process_price(self, price):
        return re.sub("\D", "", price)


class LeroyparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        article = re.sub("\D", "", item['article'])
        return f'{article}/{image_guid}.jpg'