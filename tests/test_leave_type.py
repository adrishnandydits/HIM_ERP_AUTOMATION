from pages.leave_type_page import LeaveTypePage

import pytest
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
LEAVE_TYPE_URL = "https://devanttest.in/him_test/#/human-resource/leave-type"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

LEAVE_TYPE_NAME = f"Test Leave Type {RANDOM_NUMBER}"
EDIT_LEAVE_TYPE_NAME = f"Updated Leave Type {RANDOM_NUMBER}"


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
    assert len(rows) > 0, "No leave type record added. Table body is empty."

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
        f"Exact leave type row not found. "
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
            f"Deleted leave type row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def test_leave_type_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = LeaveTypePage(driver)

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

        driver.get(LEAVE_TYPE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "leave-type" in driver.current_url.lower()

        add_step(steps, driver, "Open Leave Type Page")

        page.enter_leave_type_name(LEAVE_TYPE_NAME)
        add_step(steps, driver, "Enter Leave Type Name")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.search_leave_type(LEAVE_TYPE_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Search Leave Type")

        verify_exact_table_row_added(
            driver,
            [LEAVE_TYPE_NAME]
        )
        add_step(steps, driver, "Verify Leave Type Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.LEAVE_TYPE_NAME))
        add_step(steps, driver, "Click Edit Button")

        page.enter_leave_type_name(EDIT_LEAVE_TYPE_NAME)
        add_step(steps, driver, "Edit Leave Type Name")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.search_leave_type(EDIT_LEAVE_TYPE_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Search Updated Leave Type")

        verify_exact_table_row_added(
            driver,
            [EDIT_LEAVE_TYPE_NAME]
        )
        add_step(steps, driver, "Verify Leave Type Updated")

        page.click_delete()
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'delete')]"
                )
            )
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        page.search_leave_type(EDIT_LEAVE_TYPE_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        verify_exact_table_row_deleted(
            driver,
            [EDIT_LEAVE_TYPE_NAME]
        )
        add_step(steps, driver, "Verify Leave Type Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Leave_Type_Test_Report", steps)