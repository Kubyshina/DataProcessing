# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
# должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц
# сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. Сохраните
# в json либо csv.

from bs4 import BeautifulSoup
import requests
import json
from pprint import pprint

job = '+'.join(input("Введите название вакансии").split(' '))
pages = int(input("Введите количество страниц"))

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/97.0.4692.71 Safari/537.36'}

vacanciesDict = []
page = 0

while page < pages:
    response = requests.get(
        f'https://hh.ru/search/vacancy?area=&fromSearchLine=true&items_on_page=20&text={job}&page={page}'
        f'&hhtmFrom=vacancy_search_list',
        headers=header).text
    page += 1

    soup = BeautifulSoup(response, 'lxml')
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancyName = vacancy.find('a').text
        link = vacancy.find('a').get('href')
        salaryFrom = None
        salaryTo = None
        currency = None
        try:
            salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).text.replace('\u202f', '') \
                .split(' ')
            if "от" in salary:
                salaryFrom = int(salary[1])
                currency = salary[2]
            elif "до" in salary:
                salaryTo = int(salary[1])
                currency = salary[2]
            elif "–" in salary:
                salaryFrom = int(salary[0])
                salaryTo = int(salary[2])
                currency = salary[3]
        except:
            pass
        vacanciesDict.append([vacancyName, salaryFrom, salaryTo, currency, link])

    try:
        nextPage = soup.find('a', {'data-qa': 'pager-next'}).get('href')
    except:
        break

pprint(vacanciesDict)

with open('data.json', 'w') as file:
    json.dump(vacanciesDict, file)