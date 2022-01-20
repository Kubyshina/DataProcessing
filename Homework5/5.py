# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о
# письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pymongo import MongoClient


def getMailInfo(driver, base, prevUrl):
    mailItem = {}
    wait = WebDriverWait(driver, 30)
    wait.until(EC.url_changes(prevUrl))
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "letter-contact")))
        mailItem['sender'] = driver.find_element(By.CLASS_NAME, "letter-contact").get_attribute("title")
    except:
        mailItem['sender'] = 'Error'
    try:
        mailItem['date'] = driver.find_element(By.CLASS_NAME, "letter__date").text
    except:
        mailItem['date'] = 'Error'
    try:
        mailItem['subject'] = driver.find_element(By.CLASS_NAME, "thread-subject").text
    except:
        mailItem['subject'] = 'Error'
    try:
         mailItem['text'] = driver.find_element(By.CLASS_NAME, "letter-body__body-content").get_attribute('innerHTML')
    except:
        mailItem['text'] = 'Error'

    base.insert_one(mailItem)

from webdriver_manager.chrome import ChromeDriverManager

client = MongoClient('localhost', 27017)
db = client['mail']

mails = db.mails
db.mails.delete_many({})

driver = webdriver.Chrome()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
     "source": """
          const newProto = navigator.__proto__
          delete newProto.webdriver
          navigator.__proto__ = newProto
          """
    })
driver.get('https://mail.ru/')

elem = driver.find_element(By.CLASS_NAME, "email-input")
elem.send_keys("study.ai_172@mail.ru\n")

elem = driver.find_element(By.CLASS_NAME, "password-input")
time.sleep(1)
elem.send_keys("NextPassword172#\n")

wait = WebDriverWait(driver, 30)
prevUrl = driver.current_url
firstMailUrl = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/inbox/0:')]")))

firstMailUrl.click()

while True:
    getMailInfo(driver, mails, prevUrl)

    prevUrl = driver.current_url

    wait = WebDriverWait(driver, 30)
    nextButton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "portal-menu-element_next")))
    if driver.find_element(By.XPATH, "//div[contains(@class, 'portal-menu-element_next')]/span").get_attribute('disabled'):
        break
    nextButton.click()

print(mails.count_documents({}))

driver.quit()