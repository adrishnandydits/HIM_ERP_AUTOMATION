from pages.staff_experience_page import StaffExperiencePage

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
STAFF_EXPERIENCE_URL = "https://devanttest.in/him_test/#/staff-information/staff-experience"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"

RANDOM_NUMBER = random.randint(1000, 9999)

DESIGNATION = f"Test Designation {RANDOM_NUMBER}"
ORGANIZATION = f"Test Organization {RANDOM_NUMBER}"
EXPERIENCE = f"14{RANDOM_NUMBER}"

EDIT_DESIGNATION = f"Updated Designation {RANDOM_NUMBER}"
EDIT_ORGANIZATION = f"Updated Organization {RANDOM_NUMBER}"
EDIT_EXPERIENCE = f"24{RANDOM_NUMBER}"

FROM_DATE = "23-05-2026"
TO_DATE = "23-05-2026"

TABLE_FROM_DATE = "2026-05-23"
TABLE_TO_DATE = "2026-05-23"

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
        "//label[contains(normalize-space(),'Upload Experience Proof')]/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Staff experience proof file input was not found"

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
        "Staff experience record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Staff Experience table. "
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
        f"Exact staff experience row not found after waiting 30 seconds. "
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
        "\nStaff Experience Delete Verification Failed\n"
        "-------------------------------------------\n"
        "Expected Result : Updated staff experience row should be deleted from the table.\n"
        "Actual Result   : Updated staff experience row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_staff_experience_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_designation(DESIGNATION)
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.enter_organization(ORGANIZATION)
    page.enter_experience(EXPERIENCE)
    page.upload_experience_proof(UPLOAD_FILE_PATH)


def fill_edit_staff_experience_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_designation(EDIT_DESIGNATION)
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.enter_organization(EDIT_ORGANIZATION)
    page.enter_experience(EDIT_EXPERIENCE)
    page.upload_experience_proof(UPLOAD_FILE_PATH)


def test_staff_experience_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = StaffExperiencePage(driver)

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

        driver.get(STAFF_EXPERIENCE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "staff-experience" in driver.current_url.lower(), (
            f"Staff Experience page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Staff Experience Page")

        fill_staff_experience_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Staff Experience Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Staff Experience List")

        EXPECTED_ROW_VALUES = [
            DESIGNATION,
            ORGANIZATION,
            EXPERIENCE,
            TABLE_FROM_DATE,
            TABLE_TO_DATE
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Staff Experience Added")

        page.click_download_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download Staff Experience Proof")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_staff_experience_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Staff Experience Form")

        page.click_update()
        page.confirm_update_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")


        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Staff Experience List")

        EDIT_EXPECTED_ROW_VALUES = [
            EDIT_DESIGNATION,
            EDIT_ORGANIZATION,
            EDIT_EXPERIENCE,
            TABLE_FROM_DATE,
            TABLE_TO_DATE
        ]

        try:
            verify_exact_table_row_added(
                driver,
                EDIT_EXPECTED_ROW_VALUES
            )
            add_step(steps, driver, "Verify Staff Experience Updated")

        except Exception as update_verify_error:
            table_text = ""

            try:
                table_text = driver.find_element(By.XPATH, "//table//tbody").text
            except Exception:
                table_text = driver.find_element(By.XPATH, "//body").text

            error_reason = (
                "\nStaff Experience Update Verification Failed\n"
                "-------------------------------------------\n"
                "Expected Result : Staff experience row should show updated data after update.\n"
                "Actual Result   : Updated staff experience row was not found in the table.\n\n"
                f"Old Designation      : {DESIGNATION}\n"
                f"Expected Designation : {EDIT_DESIGNATION}\n"
                f"Old Organization     : {ORGANIZATION}\n"
                f"Expected Organization: {EDIT_ORGANIZATION}\n"
                f"Old Experience       : {EXPERIENCE}\n"
                f"Expected Experience  : {EDIT_EXPERIENCE}\n\n"
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
                "Verify Staff Experience Updated",
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
        add_step(steps, driver, "Verify Staff Experience Deleted")

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
        create_pdf_report("Staff_Experience_Test_Report", steps)