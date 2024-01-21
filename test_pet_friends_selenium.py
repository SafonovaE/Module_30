import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    # Переходим на страницу авторизации
    driver.get('https://petfriends.skillfactory.ru/login')

    yield driver

    driver.quit()

def test_show_all_pets(driver):
    driver.implicitly_wait(10)
    # Вводим email
    driver.find_element(By.ID, 'email').send_keys('testpochta@pochta.ru')
    # Вводим пароль
    driver.find_element(By.ID, 'pass').send_keys('12345')
    # Нажимаем на кнопку входа в аккаунт
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Переходим на страницу своих питомцев
    assert driver.find_element(By.TAG_NAME, 'h1')
    images = driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-img-top')
    names = driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-title')
    descriptions = driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-text')

    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ', ' in descriptions[i].text
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_show_my_pets(driver):
    # Вводим email
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "email"))
    ).send_keys('testpochta@pochta.ru')
    # Вводим пароль
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "pass"))
    ).send_keys('12345')
    # Нажимаем на кнопку входа в аккаунт
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))
    ).click()
    # Переходим на страницу своих питомцев
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/my_pets"]'))
    ).click()
    user_stats = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.\\.col-sm-4.left'))
    ).text
    pets_count_line = [s for s in user_stats.splitlines() if 'Питомцев' in s][0]
    pets_count = int(pets_count_line.split(' ')[1])
    table_rows = driver.find_elements(By.CSS_SELECTOR, 'div#all_my_pets table tbody tr')
    table_row_count = len(table_rows)
    assert pets_count == table_row_count, 'количество питомцев в таблице не соответствует указанному в статистике'
    empty_images_count = len(driver.find_elements(By.CSS_SELECTOR, 'div#all_my_pets table tbody tr th img[src=""]'))
    print(pets_count)
    print(empty_images_count)
    assert empty_images_count < pets_count / 2, 'мeнее половины питомцев имеют фото'

    pet_names = []
    pet_data = []

    for i in range(len(table_rows)):
        row = table_rows[i]
        row_data_cells = row.find_elements(By.TAG_NAME, 'td')
        pet_name = row_data_cells[0].text
        assert pet_name != '', 'не указано имя питомца'
        pet_type = row_data_cells[1].text
        assert pet_type != '', 'не указана порода'
        pet_age = row_data_cells[2].text
        assert pet_age != '', 'не указан возраст'

        pet_names.append(pet_name)
        pet_data.append(','.join([pet_name, pet_type, pet_age]))

    assert len(pet_data) == len(set(pet_data)), 'у некоторых питомцев одинаковые данные'
    assert len(pet_names) == len(set(pet_names)), 'у некоторых питомцев одинаковое имя'

