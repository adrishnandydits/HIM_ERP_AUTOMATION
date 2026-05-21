from pages.item_store_page import ItemStorePage

import pytest
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ITEM_STORE_URL = "https://devanttest.in/him_test/#/inventory/item-store"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

STORE_NAME = f"Test Store {RANDOM_NUMBER}"
ITEM_STOCK_CODE = f"TS{RANDOM_NUMBER}"
DESCRIPTION = f"Test Description {RANDOM_NUMBER}"

EDIT_STORE_NAME = f"Updated Store {RANDOM_NUMBER}"
EDIT_ITEM_STOCK_CODE = f"US{RANDOM_NUMBER}"
EDIT_DESCRIPTION = f"Updated Description {RANDOM_NUMBER}"


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


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required')]"
    )

    visible_errors = [
        error.text for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def verify_exact_table_row_added(driver, expected_values):
    import time

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + 30

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in expected_values):
                    return True

        time.sleep(1)

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact item store row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    if len(rows) == 0:
        return True

    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        assert not all(value in row_text for value in deleted_values), (
            f"Deleted item store row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def test_item_store_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ItemStorePage(driver)

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

        driver.get(ITEM_STORE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "item-store" in driver.current_url.lower(), (
            f"Item Store page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Item Store Page")

        page.enter_name(STORE_NAME)
        add_step(steps, driver, "Enter Store Name")

        page.enter_item_stock_code(ITEM_STOCK_CODE)
        add_step(steps, driver, "Enter Item Stock Code")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [STORE_NAME, ITEM_STOCK_CODE]
        )
        add_step(steps, driver, "Verify Item Store Added")

        page.click_edit_for_exact_row(
            [STORE_NAME, ITEM_STOCK_CODE]
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_name(EDIT_STORE_NAME)
        add_step(steps, driver, "Edit Store Name")

        page.enter_item_stock_code(EDIT_ITEM_STOCK_CODE)
        add_step(steps, driver, "Edit Item Stock Code")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [EDIT_STORE_NAME, EDIT_ITEM_STOCK_CODE]
        )
        add_step(steps, driver, "Verify Item Store Updated")

        page.click_delete_for_exact_row(
            [EDIT_STORE_NAME, EDIT_ITEM_STOCK_CODE]
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [EDIT_STORE_NAME, EDIT_ITEM_STOCK_CODE]
        )
        add_step(steps, driver, "Verify Item Store Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Item_Store_Test_Report", steps)