# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. Для
# парсинга использовать XPath. Структура данных должна содержать:
# - название источника;
# - наименование новости;
# - ссылку на новость;
# - дата публикации.
# Сложить собранные новости в БД
import datetime

from lxml import html
import requests
from pprint import pprint
from pymongo import MongoClient
from datetime import date, timedelta

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/97.0.4692.71 Safari/537.36'}

response = requests.get('https://yandex.ru/news/?lang=ru', headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//a[contains(text(),'Технологии')]/../../..//following-sibling::div[1]//div[contains(@class, "
                  "'mg-card_flexible')]")

client = MongoClient('localhost', 27017)
db = client['news']

collection = db.yandex_news

for item in items:
    news_item = {}
    source = item.xpath(".//a[@class='mg-card__source-link']/text()")
    title = item.xpath(".//h2[@class='mg-card__title']/a/text()")
    url = item.xpath(".//h2[@class='mg-card__title']//@href")
    news_date = item.xpath(".//span[@class='mg-card-source__time']/text()")

    news_item['source'] = source[0]
    news_item['title'] = ''.join(title).strip().replace(u'\xa0', u' ')
    news_item['url'] = url[0]

    if "вчера в " in news_date[0]:
        news_item['date'] = ' '.join([str((date.today() - timedelta(days=1))), news_date[0].trim("вчера в ")])
    else:
        news_item['date'] = ' '.join([str(date.today()), news_date[0]])

    db.collection.insert_one(news_item)


for collection_item in db.collection.find():
    pprint(collection_item)
