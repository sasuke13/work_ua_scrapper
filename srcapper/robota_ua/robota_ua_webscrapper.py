import re
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


def get_needed_cvs(categories: list, **kwargs):
    url = 'https://robota.ua/candidates/all/ukraine'

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1024)
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Переглянути')]")))

    for button in buttons:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable(button))
        element.click()

    wait = WebDriverWait(driver, 10)
    clickable_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'chevron')))

    for clickable in clickable_items:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable(clickable))

        element.click()

        preceding_elements = clickable.find_elements(By.XPATH, "ancestor::div[@data-id='cvdb-filter-language']")

        if preceding_elements:
            break


    wait = WebDriverWait(driver, 10)
    elements_to_click = [wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{item}')]")))
                         for item in categories]

    print(elements_to_click)

    for element_to_click in elements_to_click:
        actions = ActionChains(driver)
        actions.move_to_element(element_to_click).perform()
        time.sleep(10)
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable(element_to_click))
        element.click()

    time.sleep(10)


def make_request() -> BeautifulSoup:
    url = 'https://robota.ua/candidates/all/ukraine'

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1024)
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Переглянути')]")))

    for button in buttons:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable(button))
        element.click()

    wait = WebDriverWait(driver, 10)
    clickable_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'chevron')))

    for clickable in clickable_items:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable(clickable))

        element.click()

        preceding_elements = clickable.find_elements(By.XPATH, "ancestor::div[@data-id='cvdb-filter-language']")

        if preceding_elements:
            break

    # time.sleep(10)

    html = driver.page_source

    driver.quit()

    return BeautifulSoup(html, 'html.parser')


elem = make_request()
# print(elem)
# print(len(elem))
# 1770887

filter_menu = elem.find('alliance-employer-cvdb-vertical-filters-panel')

categories = filter_menu.find_all('div', {'data-id': re.compile(r'cvdb-filter-\w+')})
# print(len(categories))

# text = [category.find_next('p').strip() for category in categories]
# print(text)

language_levels = []
dct = {}

for category in categories:
    temp_list = []
    key = category.find_next('p').text.strip()
    # print(key)
    if key == 'Володіння мовами':
        levels = category.find_next('div', {'class': 'santa-ml-10 santa-px-20 ng-star-inserted'})
        language_levels = [level.text.strip() for level in levels.find_all('p')]

    inputs = category.find_all('input')

    switches = category.find_all('span', {'class': 'santa-flex-shrink-0'})

    for input in inputs:
        option = None
        next_element = input.find_next('p')

        if next_element.get('class', []) != ['santa-m-0', 'santa-typo-regular-bold', 'santa-mb-10']:
            option = next_element.text.strip()

        if key == 'Володіння мовами':
            option = {option: language_levels} if option not in language_levels else {}

        if option:
            temp_list.append(option) if option not in temp_list else None

    for switch in switches:
        temp_list.append(switch.find_previous('span').text.strip())

    if key == 'Очікувана зарплата в гривні' or key == 'Вік':
        temp_list = [temp_list[-1]] if temp_list[-1] not in temp_list[:-1] else []

    dct[key] = temp_list

print(dct)


get_needed_cvs(['IT', 'Без досвіду'], **{'Вік': [{'Від': 16}, {'До': 25}]})
