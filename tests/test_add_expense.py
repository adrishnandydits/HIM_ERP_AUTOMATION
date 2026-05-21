from pages.add_expense_page import AddExpensePage

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report

LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ADD_EXPENSE_URL = "https://devanttest.in/him_test/#/expense/add-expense"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

EXPENSE_HEAD = "IT Products"
NAME = "Mother board"
INVOICE_NUMBER = "123456789"
DATE_VALUE = "22-09-2025"
AMOUNT = "10000"
DESCRIPTION = "Replacement"


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


def test_add_expense_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AddExpensePage(driver)

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

        driver.get(ADD_EXPENSE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        assert "add-expense" in driver.current_url.lower()
        add_step(steps, driver, "Open Add Expense Page")

        page.select_expense_head()
        add_step(steps, driver, "Select Expense Head")

        page.enter_name(NAME)
        add_step(steps, driver, "Enter Expense Name")

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

        assert NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Expense Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.select_expense_head()
        add_step(steps, driver, "Edit Select Expense Head")

        page.enter_name(NAME)
        add_step(steps, driver, "Edit Expense Name")

        page.enter_invoice_number(INVOICE_NUMBER)
        add_step(steps, driver, "Edit Invoice Number")

        page.enter_date(DATE_VALUE)
        add_step(steps, driver, "Edit Date")

        page.enter_amount(AMOUNT)
        add_step(steps, driver, "Edit Amount")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        assert NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Expense Updated")

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

        add_step(steps, driver, "Verify Expense Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Add_Expense_Test_Report", steps)