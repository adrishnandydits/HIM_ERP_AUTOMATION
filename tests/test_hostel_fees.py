from pages.hostel_fees_page import HostelFeesPage

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
HOSTEL_FEES_URL = "https://devanttest.in/him_test/#/fees-collection/hostel-fees"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE_NAME = "BBA (Hospital Management)"
TYPE_NAME = "Hostel Fees"
SEMESTER_NAME = "2nd Sem"
STUDENT_NAME = "BISWAJIT GHORAI"

RANDOM_NUMBER = random.randint(1000, 9999)

AMOUNT = f"34{RANDOM_NUMBER}"
DESCRIPTION = f"Test Description {RANDOM_NUMBER}"

EDIT_AMOUNT = f"44{RANDOM_NUMBER}"
EDIT_DESCRIPTION = f"Updated Description {RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    screenshot_path = ""

    try:
        screenshot_path = take_screenshot(
            driver,
            name.lower().replace(" ", "_")
        )
    except Exception as screenshot_error:
        screenshot_path = ""

        screenshot_reason = (
            f"Screenshot failed: {type(screenshot_error).__name__}: {str(screenshot_error)}"
        )

        if reason:
            reason = f"{reason}\n{screenshot_reason}"
        else:
            reason = screenshot_reason

    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": screenshot_path
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
                f"Validation error found after submit/search: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Hostel fees record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Hostel Fees table. "
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

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Exact hostel fees row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table/page text: {table_text}"
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
        "\nHostel Fees Delete Verification Failed\n"
        "--------------------------------------\n"
        "Expected Result : Updated hostel fees row should be deleted from the table.\n"
        "Actual Result   : Updated hostel fees row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_hostel_fees_form(page):
    page.select_course_bba()
    page.select_type_hostel_fees()
    page.enter_amount(AMOUNT)
    page.enter_description(DESCRIPTION)
    page.select_grant_semester_2nd_sem()
    page.select_student_checkbox_by_name(STUDENT_NAME)


def fill_edit_hostel_fees_form(page):
    page.select_course_bba()
    page.select_type_hostel_fees()
    page.enter_amount(EDIT_AMOUNT)
    page.enter_description(EDIT_DESCRIPTION)
    page.select_grant_semester_2nd_sem()
    page.select_student_checkbox_by_name(STUDENT_NAME)


def test_hostel_fees_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = HostelFeesPage(driver)

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

        driver.get(HOSTEL_FEES_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "hostel-fees" in driver.current_url.lower(), (
            f"Hostel Fees page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Hostel Fees Page")

        fill_hostel_fees_form(page)
        add_step(steps, driver, "Fill Hostel Fees Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.search_hostel_fees_table(STUDENT_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Hostel Fees")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Hostel Fees List")

        EXPECTED_ROW_VALUES = [
            STUDENT_NAME,
            COURSE_NAME,
            SEMESTER_NAME,
            TYPE_NAME,
            AMOUNT
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Hostel Fees Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_hostel_fees_form(page)
        add_step(steps, driver, "Edit Hostel Fees Form")

        page.click_update()
        page.confirm_update_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.search_hostel_fees_table(STUDENT_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Hostel Fees")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Hostel Fees List")

        EDIT_EXPECTED_ROW_VALUES = [
            STUDENT_NAME,
            COURSE_NAME,
            SEMESTER_NAME,
            TYPE_NAME,
            EDIT_AMOUNT
        ]

        try:
            verify_exact_table_row_added(
                driver,
                EDIT_EXPECTED_ROW_VALUES
            )
            add_step(steps, driver, "Verify Hostel Fees Updated")

        except Exception as update_verify_error:
            table_text = ""

            try:
                table_text = driver.find_element(By.XPATH, "//table//tbody").text
            except Exception:
                table_text = driver.find_element(By.XPATH, "//body").text

            error_reason = (
                "\nHostel Fees Update Verification Failed\n"
                "--------------------------------------\n"
                "Expected Result : Hostel fees row should show updated amount after update.\n"
                "Actual Result   : Updated amount was not found in the table.\n\n"
                f"Old Amount      : {AMOUNT}\n"
                f"Expected Amount : {EDIT_AMOUNT}\n\n"
                "Possible Reason :\n"
                "1. Update confirmation popup was not clicked.\n"
                "2. Update API failed.\n"
                "3. Amount field was not updated before clicking Update.\n"
                "4. Table did not refresh after update.\n\n"
                f"Actual Table Text:\n{table_text}"
            )

            add_step(
                steps,
                driver,
                "Verify Hostel Fees Updated",
                "FAIL",
                reason=error_reason
            )

            raise AssertionError(error_reason)

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
        add_step(steps, driver, "Verify Hostel Fees Deleted")

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
        create_pdf_report("Hostel_Fees_Test_Report", steps)