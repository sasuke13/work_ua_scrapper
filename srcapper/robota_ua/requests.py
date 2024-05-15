import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


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
        preceding_elements = element_to_click.find_element(By.XPATH, "//precending::santa-checkbox")
        print(preceding_elements)
        element = wait.until(EC.element_to_be_clickable(element_to_click))
        element.click()

    time.sleep(10)


if __name__ == '__main__':
    get_needed_cvs(['IT', 'Без досвіду'], **{'Вік': [{'Від': 16}, {'До': 25}]})
