# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            result_salary = self.process_salary_hhru(item.get('salary'))
        else:
            print(item.get('salary'))
            result_salary = self.process_salary_superjob(item.get('salary'))
        item['salary_min'] = result_salary[0]
        item['salary_max'] = result_salary[1]
        item['currency'] = result_salary[2]
        del item['salary']
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        return item

    def process_salary_hhru(self, salary):
        if "от " in salary and " до " in salary:
            return [int(salary[1].replace('\xa0', '')), int(salary[3].replace('\xa0', '')), salary[5]]
        elif "от " in salary:
            return [int(salary[1].replace('\xa0', '')), None, salary[3]]
        elif "до " in salary:
            return [None, int(salary[1].replace('\xa0', '')), salary[3]]
        else:
            return [None, None, None]

    def process_salary_superjob(self, salary):
        if "от" in salary:
            sal = salary[2].replace('\xa0', '')
            return [int(re.sub("\D", "", sal)), None, re.sub("\d", "", sal)]
        elif "до" in salary:
            sal = salary[2].replace('\xa0', '')
            return [None, int(re.sub("\D", "", sal)), re.sub("\d", "", sal)]
        elif "По договорённости" in salary:
            return [None, None, None]
        else:
            return [int(salary[0].replace('\xa0', '')), int(salary[1].replace('\xa0', '')), salary[3]]
