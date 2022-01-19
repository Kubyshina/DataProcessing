# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
# только новые вакансии/продукты в вашу базу.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты).

from bs4 import BeautifulSoup
import requests
import json
from pprint import pprint
from pymongo import MongoClient, TEXT
import re


def addVacancies(jobTitle, pagesCount, collection):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/97.0.4692.71 Safari/537.36'}
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
            vacancy_item = {}
            vacancy_item['vacancyName'] = vacancy.find('a').text
            vacancy_item['link'] = vacancy.find('a').get('href')
            vacancy_item['id'] = re.search('(\d+)', vacancy_item['link']).group(0)
            vacancy_item['salaryFrom'] = None
            vacancy_item['salaryTo'] = None
            vacancy_item['currency'] = None
            try:
                salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).text.replace('\u202f',
                                                                                                              '') \
                    .split(' ')
                if "от" in salary:
                    vacancy_item['salaryFrom'] = int(salary[1])
                    vacancy_item['currency'] = salary[2]
                elif "до" in salary:
                    vacancy_item['salaryTo'] = int(salary[1])
                    vacancy_item['currency'] = salary[2]
                elif "–" in salary:
                    vacancy_item['salaryFrom'] = int(salary[0])
                    vacancy_item['salaryTo'] = int(salary[2])
                    vacancy_item['currency'] = salary[3]
            except:
                pass
            try:
                collection.insert_one(vacancy_item)
            except:
                pass

        try:
            soup.find('a', {'data-qa': 'pager-next'}).get('href')
        except:
            break


def getVacanciesBySalary(salary, collection):
    for vacancy in collection.find({'$or': [{'salaryFrom': {'$gt': salary}}, {'salaryTo': {'$gt': salary}}]}):
        pprint(vacancy)


job = '+'.join(input("Введите название вакансии").split(' '))
pages = int(input("Введите количество страниц"))

client = MongoClient('localhost', 27017)
db = client['hh']

vacancies = db.vacancies
vacancies.create_index([('id', TEXT)], name='unique_id', unique=True)
addVacancies(job, pages, vacancies)
getVacanciesBySalary(300000, vacancies)

# for vacancy in vacancies.find({}):
#    pprint(vacancy)

# print(vacancies.count_documents({}))
