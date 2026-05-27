from pages.subject_page import SubjectPage

import pytest
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
SUBJECT_URL = "https://devanttest.in/him_test/#/academics/subject"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

SUBJECT_NAME = f"Test Subject {RANDOM_NUMBER}"
SUBJECT_CATEGORY = f"Test Category {RANDOM_NUMBER}"
SUBJECT_CODE = f"TS{RANDOM_NUMBER}"

EDIT_SUBJECT_NAME = f"Updated Subject {RANDOM_NUMBER}"
EDIT_SUBJECT_CATEGORY = f"Updated Category {RANDOM_NUMBER}"
EDIT_SUBJECT_CODE = f"US{RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
    )

    visible_errors = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_table_or_validation(driver, timeout=30):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
            return True

        errors = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
        )

        visible_errors = [
            error.text.strip()
            for error in errors
            if error.is_displayed() and error.text.strip()
        ]

        if visible_errors:
            raise AssertionError(
                f"Validation error found after submit: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Subject record was not added. "
        "After clicking Submit, no row appeared in the Subject List table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


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
        f"Exact subject row not found after waiting 30 seconds. "
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
        "\nSubject Delete Verification Failed\n"
        "----------------------------------\n"
        "Expected Result : Updated subject row should be deleted from the table.\n"
        "Actual Result   : Updated subject row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_subject_form(page, subject_name, subject_category, subject_code):
    page.enter_subject_name(subject_name)
    page.enter_subject_category(subject_category)
    page.enter_subject_code(subject_code)


def test_subject_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SubjectPage(driver)

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

        driver.get(SUBJECT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "subject" in driver.current_url.lower(), (
            f"Subject page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Subject Page")

        fill_subject_form(
            page,
            SUBJECT_NAME,
            SUBJECT_CATEGORY,
            SUBJECT_CODE
        )
        add_step(steps, driver, "Fill Subject Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Subject List")

        page.search_subject(SUBJECT_CODE)
        add_step(steps, driver, "Search Added Subject")

        EXPECTED_ROW_VALUES = [
            SUBJECT_NAME,
            SUBJECT_CODE
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Subject Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_subject_form(
            page,
            EDIT_SUBJECT_NAME,
            EDIT_SUBJECT_CATEGORY,
            EDIT_SUBJECT_CODE
        )
        add_step(steps, driver, "Edit Subject Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait.until(EC.presence_of_element_located(page.TABLE_SEARCH))
        page.search_subject(EDIT_SUBJECT_CODE)
        add_step(steps, driver, "Search Updated Subject")

        EDIT_EXPECTED_ROW_VALUES = [
            EDIT_SUBJECT_NAME,
            EDIT_SUBJECT_CODE
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Subject Updated")

        page.click_delete_for_exact_row(
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Subject Deleted")

    except Exception as e:
        error_reason = str(e).strip()

        if not error_reason:
            error_reason = "No detailed error message returned by Selenium."

        error_reason = f"{type(e).__name__}: {error_reason}"

        try:
            add_step(
                steps,
                driver,
                "Test Failed",
                "FAIL",
                reason=error_reason
            )
        except Exception:
            steps.append({
                "name": "Test Failed",
                "status": "FAIL",
                "reason": error_reason,
                "image": ""
            })

        raise e

    finally:
        create_pdf_report("Subject_Test_Report", steps)
