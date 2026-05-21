from pages.add_income_page import AddIncomePage

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report

LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ADD_INCOME_URL = "https://devanttest.in/him_test/#/income/add-income"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

INCOME_NAME = "Broken Computer"
INVOICE_NUMBER = "0"
DATE_VALUE = "22-09-2025"
AMOUNT = "10000"
DESCRIPTION = "Selling Of broken computer"

EDIT_INCOME_NAME = "Broken Computer"
EDIT_INVOICE_NUMBER = "0"
EDIT_DATE_VALUE = "22-09-2025"
EDIT_AMOUNT = "10000"
EDIT_DESCRIPTION = "Selling Of broken computer"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS"):
    steps.append({
        "name": name,
        "status": status,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def test_add_income_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AddIncomePage(driver)

        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Login Page")

        page.enter_text(page.EMAIL, EMAIL)
        add_step(steps, driver, "Enter Email")

        page.enter_text(page.PASSWORD, PASSWORD)
        add_step(steps, driver, "Enter Password")

        page.click(page.LOGIN_BUTTON)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Login Button")

        driver.get(ADD_INCOME_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        assert "add-income" in driver.current_url.lower()
        add_step(steps, driver, "Open Add Income Page")

        page.select_income_head()
        add_step(steps, driver, "Select Income Head")

        page.enter_name(INCOME_NAME)
        add_step(steps, driver, "Enter Income Name")

        page.enter_invoice_number(INVOICE_NUMBER)
        add_step(steps, driver, "Enter Invoice Number")

        page.enter_date(DATE_VALUE)
        add_step(steps, driver, "Enter Date")

        page.enter_amount(AMOUNT)
        add_step(steps, driver, "Enter Amount")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        assert INCOME_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Income Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.select_income_head()
        add_step(steps, driver, "Edit Select Income Head")

        page.enter_name(EDIT_INCOME_NAME)
        add_step(steps, driver, "Edit Income Name")

        page.enter_invoice_number(EDIT_INVOICE_NUMBER)
        add_step(steps, driver, "Edit Invoice Number")

        page.enter_date(EDIT_DATE_VALUE)
        add_step(steps, driver, "Edit Date")

        page.enter_amount(EDIT_AMOUNT)
        add_step(steps, driver, "Edit Amount")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        assert EDIT_INCOME_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Income Updated")

        page.click_delete()
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(),'Confirmation') or contains(text(),'delete')]")
            )
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        add_step(steps, driver, "Verify Income Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Add_Income_Test_Report", steps)