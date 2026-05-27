from pages.examiners_page import ExaminersPage

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
EXAMINERS_URL = "https://devanttest.in/him_test/#/staff-information/examiners"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"

RANDOM_NUMBER = random.randint(1000, 9999)

EXAMINATION_NAME = f"Test Examination {RANDOM_NUMBER}"
TYPE_OF_EXAMINER = f"Test Examiner {RANDOM_NUMBER}"
UNIVERSITY_NAME = f"Test University {RANDOM_NUMBER}"
REFERENCE_NO = f"57{RANDOM_NUMBER}"

EDIT_EXAMINATION_NAME = f"Updated Examination {RANDOM_NUMBER}"
EDIT_TYPE_OF_EXAMINER = f"Updated Examiner {RANDOM_NUMBER}"
EDIT_UNIVERSITY_NAME = f"Updated University {RANDOM_NUMBER}"
EDIT_REFERENCE_NO = f"67{RANDOM_NUMBER}"

EXAMINER_DATE = "23-05-2026"
SEARCH_FROM_DATE = "23-05-2026"
SEARCH_TO_DATE = "23-05-2026"

TABLE_DATE = "2026-05-23"

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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Examiner upload file input was not found"

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
        "Examiner record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Examiner table. "
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
        f"Exact examiner row not found after waiting 30 seconds. "
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
        "\nExaminer Delete Verification Failed\n"
        "-----------------------------------\n"
        "Expected Result : Updated examiner row should be deleted from the table.\n"
        "Actual Result   : Updated examiner row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_examiner_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_examination_name(EXAMINATION_NAME)
    page.enter_type_of_examiner(TYPE_OF_EXAMINER)
    page.enter_university_name(UNIVERSITY_NAME)
    page.enter_reference_no(REFERENCE_NO)
    page.enter_examiner_date(EXAMINER_DATE)
    page.upload_file(UPLOAD_FILE_PATH)


def fill_edit_examiner_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_examination_name(EDIT_EXAMINATION_NAME)
    page.enter_type_of_examiner(EDIT_TYPE_OF_EXAMINER)
    page.enter_university_name(EDIT_UNIVERSITY_NAME)
    page.enter_reference_no(EDIT_REFERENCE_NO)
    page.enter_examiner_date(EXAMINER_DATE)
    page.upload_file(UPLOAD_FILE_PATH)


def test_examiners_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ExaminersPage(driver)

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

        driver.get(EXAMINERS_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "examiners" in driver.current_url.lower(), (
            f"Examiners page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Examiners Page")

        page.click_add_examiners()
        add_step(steps, driver, "Click Add Examiners")

        fill_examiner_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Examiners Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        page.click_show_examiners()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Examiners")

        page.search_examiner(
            SEARCH_FROM_DATE,
            SEARCH_TO_DATE,
            STAFF_NAME
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Examiner")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Examiner List")

        EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            EXAMINATION_NAME,
            TYPE_OF_EXAMINER,
            UNIVERSITY_NAME,
            REFERENCE_NO,
            TABLE_DATE
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Examiner Added")

        page.click_download_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download Examiner File")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_examiner_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Examiners Form")

        page.click_update()
        page.confirm_update_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        page.click_show_examiners()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Examiners")

        page.search_examiner(
            SEARCH_FROM_DATE,
            SEARCH_TO_DATE,
            STAFF_NAME
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Examiner")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Examiner List")

        EDIT_EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            EDIT_EXAMINATION_NAME,
            EDIT_TYPE_OF_EXAMINER,
            EDIT_UNIVERSITY_NAME,
            EDIT_REFERENCE_NO,
            TABLE_DATE
        ]

        try:
            verify_exact_table_row_added(
                driver,
                EDIT_EXPECTED_ROW_VALUES
            )
            add_step(steps, driver, "Verify Examiner Updated")

        except Exception as update_verify_error:
            table_text = ""

            try:
                table_text = driver.find_element(By.XPATH, "//table//tbody").text
            except Exception:
                table_text = driver.find_element(By.XPATH, "//body").text

            error_reason = (
                "\nExaminer Update Verification Failed\n"
                "-----------------------------------\n"
                "Expected Result : Examiner row should show updated data after update.\n"
                "Actual Result   : Updated examiner row was not found in the table.\n\n"
                f"Old Examination Name      : {EXAMINATION_NAME}\n"
                f"Expected Examination Name : {EDIT_EXAMINATION_NAME}\n"
                f"Old Type Of Examiner      : {TYPE_OF_EXAMINER}\n"
                f"Expected Type Of Examiner : {EDIT_TYPE_OF_EXAMINER}\n"
                f"Old University Name       : {UNIVERSITY_NAME}\n"
                f"Expected University Name  : {EDIT_UNIVERSITY_NAME}\n"
                f"Old Reference No          : {REFERENCE_NO}\n"
                f"Expected Reference No     : {EDIT_REFERENCE_NO}\n\n"
                "Possible Reason :\n"
                "1. Update confirmation popup was not clicked.\n"
                "2. Update API failed.\n"
                "3. Form fields were not updated before clicking Update.\n"
                "4. Table did not refresh after update.\n\n"
                f"Actual Table Text:\n{table_text}"
            )

            add_step(
                steps,
                driver,
                "Verify Examiner Updated",
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
        add_step(steps, driver, "Verify Examiner Deleted")

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
        create_pdf_report("Examiners_Test_Report", steps)