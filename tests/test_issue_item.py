from pages.issue_item_page import IssueItemPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ISSUE_ITEM_URL = "https://devanttest.in/him_test/#/inventory/issue-item"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

ISSUE_DATE = "01-05-2026"
RETURN_DATE = "14-05-2026"
QUANTITY = "2"


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
        f"Exact issue item row not found after waiting 30 seconds. "
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
        "\nIssue Item Delete Verification Failed\n"
        "-------------------------------------\n"
        "Expected Result : Issue item row should be deleted from the table.\n"
        "Actual Result   : Issue item row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def test_issue_item_add_return_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = IssueItemPage(driver)

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

        driver.get(ISSUE_ITEM_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "issue-item" in driver.current_url.lower(), (
            f"Issue Item page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Issue Item Page")

        page.click_issue_item_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Issue Item Tab")

        SELECTED_USER_TYPE = page.select_user_type_teacher()
        add_step(steps, driver, "Select User Type")

        SELECTED_ISSUED_TO = page.select_issued_to()
        add_step(steps, driver, "Select Issued To")

        SELECTED_ISSUED_BY = page.select_issued_by()
        add_step(steps, driver, "Select Issued By")

        page.enter_issue_date(ISSUE_DATE)
        add_step(steps, driver, "Enter Issue Date")

        page.enter_return_date(RETURN_DATE)
        add_step(steps, driver, "Enter Return Date")

        SELECTED_CATEGORY = page.select_item_category_vehicles()
        add_step(steps, driver, "Select Item Category")

        time.sleep(2)

        SELECTED_ITEM = page.select_item_bus()
        add_step(steps, driver, "Select Item")

        page.enter_quantity(QUANTITY)
        add_step(steps, driver, "Enter Quantity")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_issued_item_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Issued Item Tab")

        EXPECTED_ROW_VALUES = [
            SELECTED_CATEGORY,
            SELECTED_ISSUED_TO,
            SELECTED_ISSUED_BY,
            QUANTITY
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Issue Item Added")

        page.click_return_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Return Button")

        page.confirm_return()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Return")

        page.click_delete_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Issue Item Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Issue_Item_Test_Report", steps)