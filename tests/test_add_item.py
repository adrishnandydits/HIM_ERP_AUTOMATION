from pages.add_item_page import AddItemPage

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report

LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ADD_ITEM_URL = "https://devanttest.in/him_test/#/inventory/add-item"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

ITEM_NAME = "test item"
ITEM_TYPE = "IT"
UNIT = "10"
DESCRIPTION = "testing"

EDIT_ITEM_NAME = "abcd"
EDIT_ITEM_TYPE = "table"
EDIT_UNIT = "10"
EDIT_DESCRIPTION = "testing"


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
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No item added. Table body is empty."

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        if all(value in row_text for value in expected_values):
            return True

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact item row not found. "
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
            f"Deleted item row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def test_add_item_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AddItemPage(driver)

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

        driver.get(ADD_ITEM_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        assert "add-item" in driver.current_url.lower()
        add_step(steps, driver, "Open Add Item Page")

        page.enter_name(ITEM_NAME)
        add_step(steps, driver, "Enter Item Name")

        page.select_item_type()
        add_step(steps, driver, "Select Item Type")

        page.enter_unit(UNIT)
        add_step(steps, driver, "Enter Unit")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)
        verify_exact_table_row_added(
            driver,
            [ITEM_NAME, ITEM_TYPE, UNIT, DESCRIPTION]
        )
        add_step(steps, driver, "Verify Item Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_name(EDIT_ITEM_NAME)
        add_step(steps, driver, "Edit Item Name")

        page.select_item_type()
        add_step(steps, driver, "Edit Select Item Type")

        page.enter_unit(EDIT_UNIT)
        add_step(steps, driver, "Edit Unit")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)
        verify_exact_table_row_added(
            driver,
            [EDIT_ITEM_NAME, EDIT_UNIT, EDIT_DESCRIPTION]
        )
        add_step(steps, driver, "Verify Item Updated")

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

        verify_exact_table_row_deleted(
            driver,
            [EDIT_ITEM_NAME, EDIT_UNIT, EDIT_DESCRIPTION]
        )
        add_step(steps, driver, "Verify Item Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Add_Item_Test_Report", steps)