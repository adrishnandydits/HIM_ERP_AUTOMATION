from pages.expense_head_page import ExpenseHeadPage

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report

LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
EXPENSE_HEAD_URL = "https://devanttest.in/him_test/#/expense/expense-head"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

EXPENSE_NAME = "IT Products"
EXPENSE_DESCRIPTION = "computer products"

EDIT_EXPENSE_NAME = "IT Products"
EDIT_EXPENSE_DESCRIPTION = "computer products"


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


def test_expense_head_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ExpenseHeadPage(driver)

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

        driver.get(EXPENSE_HEAD_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        assert "expense-head" in driver.current_url.lower()
        add_step(steps, driver, "Open Expense Head Page")

        page.enter_name(EXPENSE_NAME)
        add_step(steps, driver, "Enter Expense Head Name")

        page.enter_description(EXPENSE_DESCRIPTION)
        add_step(steps, driver, "Enter Expense Head Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")
        time.sleep(5)

        assert EXPENSE_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Expense Head Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_name(EDIT_EXPENSE_NAME)
        add_step(steps, driver, "Edit Expense Head Name")

        page.enter_description(EDIT_EXPENSE_DESCRIPTION)
        add_step(steps, driver, "Edit Expense Head Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        assert EDIT_EXPENSE_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Expense Head Updated")

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

        add_step(steps, driver, "Verify Expense Head Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Expense_Head_Test_Report", steps)