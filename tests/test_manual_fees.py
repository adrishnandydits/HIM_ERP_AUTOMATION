from pages.manual_fees_page import ManualFeesPage

import os
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
MANUAL_FEES_URL = "https://devanttest.in/him_test/#/fees-collection/manual-fees"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE_NAME = "BBA (Hospital Management)"
SEMESTER_NAME = "2nd Sem"
STUDENT_NAME = "MAINAK MONDAL"

RANDOM_NUMBER = random.randint(1000, 9999)

DATE_OF_PAYMENT = "23-05-2026"
SEARCH_DATE = "23-05-2026"

AMOUNT = f"42{RANDOM_NUMBER}"
EDIT_AMOUNT = f"52{RANDOM_NUMBER}"

UPLOAD_FILE_PATH = r"C:\Users\Devant\Downloads\Group 3621 (5).png"


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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(
        By.XPATH,
        "//label[contains(normalize-space(),'Upload Slip')]/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Manual fees upload slip file input was not found"

    return True


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
        "Manual fees record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Manual Fees table. "
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
        f"Exact manual fees row not found after waiting 30 seconds. "
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
        "\nManual Fees Delete Verification Failed\n"
        "--------------------------------------\n"
        "Expected Result : Updated manual fees row should be deleted from the table.\n"
        "Actual Result   : Updated manual fees row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_manual_fees_form(page):
    page.select_course_bba()
    page.select_semester_2nd_sem()
    page.wait_for_student_options()
    page.select_student_by_name(STUDENT_NAME)
    page.enter_date_of_payment(DATE_OF_PAYMENT)
    page.enter_amount(AMOUNT)
    page.upload_slip(UPLOAD_FILE_PATH)


def fill_edit_manual_fees_form(page):
    page.select_course_bba()
    page.select_semester_2nd_sem()
    page.wait_for_student_options()
    page.select_student_by_name(STUDENT_NAME)
    page.enter_date_of_payment(DATE_OF_PAYMENT)
    page.enter_amount(EDIT_AMOUNT)
    page.upload_slip(UPLOAD_FILE_PATH)


def test_manual_fees_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ManualFeesPage(driver)

        assert os.path.exists(UPLOAD_FILE_PATH), (
            f"Upload file does not exist: {UPLOAD_FILE_PATH}"
        )

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

        driver.get(MANUAL_FEES_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "manual-fees" in driver.current_url.lower(), (
            f"Manual Fees page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Manual Fees Page")

        page.click_add_manual_fees()
        add_step(steps, driver, "Click Add Manual Fees")

        fill_manual_fees_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Manual Fees Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_manual_fees()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Manual Fees")

        page.search_manual_fees(
            SEARCH_DATE,
            SEARCH_DATE
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Manual Fees")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Manual Fees List")

        EXPECTED_ROW_VALUES = [
            STUDENT_NAME,
            COURSE_NAME,
            SEMESTER_NAME,
            AMOUNT
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Manual Fees Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_manual_fees_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Manual Fees Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.click_show_manual_fees()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Manual Fees")

        page.search_manual_fees(
            SEARCH_DATE,
            SEARCH_DATE
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Manual Fees")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Manual Fees List")

        EDIT_EXPECTED_ROW_VALUES = [
            STUDENT_NAME,
            COURSE_NAME,
            SEMESTER_NAME,
            EDIT_AMOUNT
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Manual Fees Updated")

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
        add_step(steps, driver, "Verify Manual Fees Deleted")

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
        create_pdf_report("Manual_Fees_Test_Report", steps)