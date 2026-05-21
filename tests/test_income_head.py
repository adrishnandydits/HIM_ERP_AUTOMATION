from pages.income_head_page import IncomeHeadPage

import pytest
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
INCOME_HEAD_URL = "https://devanttest.in/him_test/#/income/income-head"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"


def random_text(prefix, length=8):
    random_part = ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
    return f"{prefix} {random_part}"


ADD_NAME = random_text("Income Head")
ADD_DESCRIPTION = random_text("Income Head Description", 15)

EDIT_NAME = random_text("Updated Income Head")
EDIT_DESCRIPTION = random_text("Updated Income Head Description", 15)


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
        "image": take_screenshot(
            driver,
            name.lower().replace(" ", "_")
        )
    })


def wait_for_text(wait, text):
    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[contains("
                f"translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                f"'{text.lower()}')]"
            )
        )
    )


def test_income_head_add_edit_delete(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = IncomeHeadPage(driver)

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

        driver.get(INCOME_HEAD_URL)
        wait.until(EC.url_contains("income-head"))
        assert "income-head" in driver.current_url.lower()
        add_step(steps, driver, "Open Income Head Page")

        page.enter_income_name(ADD_NAME)
        add_step(steps, driver, "Enter Income Head Name")

        page.enter_income_description(ADD_DESCRIPTION)
        add_step(steps, driver, "Enter Income Head Description")

        page.click_submit()
        wait_for_text(wait, ADD_NAME)
        add_step(steps, driver, "Click Submit Button")

        assert ADD_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Income Head Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_income_name(EDIT_NAME)
        add_step(steps, driver, "Edit Income Head Name")

        page.enter_income_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Income Head Description")

        page.click_update()
        wait_for_text(wait, EDIT_NAME)
        add_step(steps, driver, "Click Update Button")

        assert EDIT_NAME.lower() in driver.page_source.lower()
        add_step(steps, driver, "Verify Income Head Updated")

        page.click_delete()
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(text(),'Confirmation') "
                    "or contains(text(),'delete') "
                    "or contains(text(),'Delete')]"
                )
            )
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(
            lambda d: EDIT_NAME.lower() not in d.page_source.lower()
        )
        add_step(steps, driver, "Confirm Delete")

        assert EDIT_NAME.lower() not in driver.page_source.lower()
        add_step(steps, driver, "Verify Income Head Deleted")

    except Exception:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise

    finally:
        create_pdf_report("Income_Head_Test_Report", steps)