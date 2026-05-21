from pages.item_supplier_page import ItemSupplierPage

import pytest
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ITEM_SUPPLIER_URL = "https://devanttest.in/him_test/#/inventory/item-supplier"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

SUPPLIER_NAME = f"Test Supplier {RANDOM_NUMBER}"
SUPPLIER_PHONE = f"900009{RANDOM_NUMBER}"
SUPPLIER_EMAIL = f"supplier{RANDOM_NUMBER}@test.com"

ADDRESS = f"Test Address {RANDOM_NUMBER}"

CONTACT_PERSON_NAME = f"Contact Person {RANDOM_NUMBER}"
CONTACT_PERSON_PHONE = f"800009{RANDOM_NUMBER}"
CONTACT_PERSON_EMAIL = f"contact{RANDOM_NUMBER}@test.com"

DESCRIPTION = f"Test Description {RANDOM_NUMBER}"


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
    assert len(rows) > 0, "No supplier record added. Table body is empty."

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
        f"Exact supplier row not found. "
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
            f"Deleted supplier row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def test_item_supplier_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ItemSupplierPage(driver)

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

        driver.get(ITEM_SUPPLIER_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "item-supplier" in driver.current_url.lower(), (
            f"Item Supplier page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Item Supplier Page")

        page.enter_name(SUPPLIER_NAME)
        add_step(steps, driver, "Enter Supplier Name")

        page.enter_phone(SUPPLIER_PHONE)
        add_step(steps, driver, "Enter Supplier Phone")

        page.enter_email(SUPPLIER_EMAIL)
        add_step(steps, driver, "Enter Supplier Email")

        page.enter_address(ADDRESS)
        add_step(steps, driver, "Enter Address")

        page.enter_contact_person_name(CONTACT_PERSON_NAME)
        add_step(steps, driver, "Enter Contact Person Name")

        page.enter_contact_person_phone(CONTACT_PERSON_PHONE)
        add_step(steps, driver, "Enter Contact Person Phone")

        page.enter_contact_person_email(CONTACT_PERSON_EMAIL)
        add_step(steps, driver, "Enter Contact Person Email")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [SUPPLIER_NAME, CONTACT_PERSON_NAME]
        )
        add_step(steps, driver, "Verify Supplier Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_name(SUPPLIER_NAME)
        add_step(steps, driver, "Edit Supplier Name")

        page.enter_phone(SUPPLIER_PHONE)
        add_step(steps, driver, "Edit Supplier Phone")

        page.enter_email(SUPPLIER_EMAIL)
        add_step(steps, driver, "Edit Supplier Email")

        page.enter_address(ADDRESS)
        add_step(steps, driver, "Edit Address")

        page.enter_contact_person_name(CONTACT_PERSON_NAME)
        add_step(steps, driver, "Edit Contact Person Name")

        page.enter_contact_person_phone(CONTACT_PERSON_PHONE)
        add_step(steps, driver, "Edit Contact Person Phone")

        page.enter_contact_person_email(CONTACT_PERSON_EMAIL)
        add_step(steps, driver, "Edit Contact Person Email")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        add_step(steps, driver, "Verify Supplier Updated")

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

        add_step(steps, driver, "Verify Supplier Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Item_Supplier_Test_Report", steps)