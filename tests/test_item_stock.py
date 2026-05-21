from pages.item_stock_page import ItemStockPage

import pytest
import random
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ITEM_STOCK_URL = "https://devanttest.in/him_test/#/inventory/item-stock"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

QUANTITY = str(random.randint(10, 99))
DATE = "13-05-2026"
PURCHASE_PRICE = str(random.randint(500, 5000))
DESCRIPTION = f"Test Description {RANDOM_NUMBER}"

EDIT_QUANTITY = str(random.randint(100, 199))
EDIT_DATE = "13-05-2026"
EDIT_PURCHASE_PRICE = str(random.randint(6000, 9000))
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
        f"Exact item stock row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values):
    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    end_time = time.time() + 30
    matching_row_text = ""

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        deleted_row_found = False

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in deleted_values):
                deleted_row_found = True
                matching_row_text = row.text
                break

        if not deleted_row_found:
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nItem Stock Delete Verification Failed\n"
        "-------------------------------------\n"
        "Expected Result : Updated item stock row should be deleted from the table.\n"
        "Actual Result   : Updated item stock row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def test_item_stock_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ItemStockPage(driver)

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

        driver.get(ITEM_STOCK_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "item-stock" in driver.current_url.lower(), (
            f"Item Stock page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Item Stock Page")

        SELECTED_CATEGORY = page.select_item_category()
        add_step(steps, driver, "Select Item Category")

        time.sleep(2)

        SELECTED_ITEM = page.select_item()
        add_step(steps, driver, "Select Item")

        SELECTED_SUPPLIER = page.select_supplier()
        add_step(steps, driver, "Select Supplier")

        SELECTED_STORE = page.select_store()
        add_step(steps, driver, "Select Store")

        page.enter_quantity(QUANTITY)
        add_step(steps, driver, "Enter Quantity")

        page.enter_date(DATE)
        add_step(steps, driver, "Enter Date")

        page.enter_purchase_price(PURCHASE_PRICE)
        add_step(steps, driver, "Enter Purchase Price")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [SELECTED_ITEM, SELECTED_SUPPLIER, SELECTED_STORE, PURCHASE_PRICE, QUANTITY]
        )
        add_step(steps, driver, "Verify Item Stock Added")

        page.click_edit_for_exact_row(
            [SELECTED_ITEM, SELECTED_SUPPLIER, SELECTED_STORE, PURCHASE_PRICE, QUANTITY]
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        EDIT_SELECTED_CATEGORY = page.select_item_category()
        add_step(steps, driver, "Edit Item Category")

        time.sleep(2)

        EDIT_SELECTED_ITEM = page.select_item()
        add_step(steps, driver, "Edit Item")

        EDIT_SELECTED_SUPPLIER = page.select_supplier()
        add_step(steps, driver, "Edit Supplier")

        EDIT_SELECTED_STORE = page.select_store()
        add_step(steps, driver, "Edit Store")

        page.enter_quantity(EDIT_QUANTITY)
        add_step(steps, driver, "Edit Quantity")

        page.enter_date(EDIT_DATE)
        add_step(steps, driver, "Edit Date")

        page.enter_purchase_price(EDIT_PURCHASE_PRICE)
        add_step(steps, driver, "Edit Purchase Price")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [
                EDIT_SELECTED_ITEM,
                EDIT_SELECTED_SUPPLIER,
                EDIT_SELECTED_STORE,
                EDIT_PURCHASE_PRICE,
                EDIT_QUANTITY
            ]
        )
        add_step(steps, driver, "Verify Item Stock Updated")

        page.click_delete_for_exact_row(
            [
                EDIT_SELECTED_ITEM,
                EDIT_SELECTED_SUPPLIER,
                EDIT_SELECTED_STORE,
                EDIT_PURCHASE_PRICE,
                EDIT_QUANTITY
            ]
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [
                EDIT_SELECTED_ITEM,
                EDIT_SELECTED_SUPPLIER,
                EDIT_SELECTED_STORE,
                EDIT_PURCHASE_PRICE,
                EDIT_QUANTITY
            ]
        )
        add_step(steps, driver, "Verify Item Stock Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Item_Stock_Test_Report", steps)