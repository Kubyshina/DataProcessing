# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
import requests
import json

req = requests.get("https://api.github.com/users/kubyshina/repos")

with open('repos.json', 'w') as outfile:
    json.dump(req.text, outfile)

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
import requests
import pickle
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Client-Id':'234896',
                    'Api-Key':'1843572b-hgb7-4229-a8e3-b4s30535eb0f'}
req = requests.get('https://api-seller.ozon.ru/v1/categories/tree',headers=headers)

print(req)
with open('response.json', 'w') as outfile:
    json.dump(req.text, outfile)