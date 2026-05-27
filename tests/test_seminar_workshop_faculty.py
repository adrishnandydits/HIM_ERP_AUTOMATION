from pages.seminar_workshop_faculty_page import SeminarWorkshopFacultyPage

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
SEMINAR_WORKSHOP_FACULTY_URL = "https://devanttest.in/him_test/#/staff-information/seminar-workshop-faculty"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"

RANDOM_NUMBER = random.randint(1000, 9999)

TITLE = f"Test Seminar {RANDOM_NUMBER}"
TYPE = f"Test Workshop {RANDOM_NUMBER}"
ORGANIZED_BY = f"Test Organizer {RANDOM_NUMBER}"
DURATION = "1"
ACHIEVEMENT = f"Test Achievement {RANDOM_NUMBER}"

EDIT_TITLE = f"Updated Seminar {RANDOM_NUMBER}"
EDIT_TYPE = f"Updated Workshop {RANDOM_NUMBER}"
EDIT_ORGANIZED_BY = f"Updated Organizer {RANDOM_NUMBER}"
EDIT_DURATION = "2"
EDIT_ACHIEVEMENT = f"Updated Achievement {RANDOM_NUMBER}"

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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Seminar upload file input was not found"

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
        "Seminar / Workshop / Faculty Development Programme record was not loaded. "
        "After clicking Submit/Search, no row appeared in the table. "
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
        f"Exact seminar row not found after waiting 30 seconds. "
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
        "\nSeminar Delete Verification Failed\n"
        "----------------------------------\n"
        "Expected Result : Updated seminar row should be deleted from the table.\n"
        "Actual Result   : Updated seminar row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_seminar_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_title(TITLE)
    page.enter_type(TYPE)
    page.enter_organized_by(ORGANIZED_BY)
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.enter_achievement(ACHIEVEMENT)
    page.upload_file(UPLOAD_FILE_PATH)


def fill_edit_seminar_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_title(EDIT_TITLE)
    page.enter_type(EDIT_TYPE)
    page.enter_organized_by(EDIT_ORGANIZED_BY)
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.enter_achievement(EDIT_ACHIEVEMENT)
    page.upload_file(UPLOAD_FILE_PATH)


def test_seminar_workshop_faculty_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SeminarWorkshopFacultyPage(driver)

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

        driver.get(SEMINAR_WORKSHOP_FACULTY_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "seminar-workshop-faculty" in driver.current_url.lower(), (
            f"Seminar / Workshop / Faculty page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Seminar Workshop Faculty Page")

        page.click_add_tab()
        add_step(steps, driver, "Click Add Tab")

        fill_seminar_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Seminar Workshop Faculty Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        page.click_show_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Tab")

        page.search_seminar(
            FROM_DATE,
            TO_DATE,
            STAFF_NAME
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Seminar Workshop Faculty")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Seminar Workshop Faculty List")

        EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            TITLE,
            TYPE,
            ORGANIZED_BY,
            DURATION,
            TABLE_FROM_DATE,
            TABLE_TO_DATE,
            ACHIEVEMENT
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Seminar Workshop Faculty Added")

        page.click_download_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download Seminar File")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_seminar_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Seminar Workshop Faculty Form")

        page.click_update()
        page.confirm_update_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        page.click_show_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Seminar Workshop Faculty")

        page.search_seminar(
            FROM_DATE,
            TO_DATE,
            STAFF_NAME
        )
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Seminar Workshop Faculty")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Seminar Workshop Faculty List")

        EDIT_EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            EDIT_TITLE,
            EDIT_TYPE,
            EDIT_ORGANIZED_BY,
            EDIT_DURATION,
            TABLE_FROM_DATE,
            TABLE_TO_DATE,
            EDIT_ACHIEVEMENT
        ]

        try:
            verify_exact_table_row_added(
                driver,
                EDIT_EXPECTED_ROW_VALUES
            )
            add_step(steps, driver, "Verify Seminar Workshop Faculty Updated")

        except Exception as update_verify_error:
            table_text = ""

            try:
                table_text = driver.find_element(By.XPATH, "//table//tbody").text
            except Exception:
                table_text = driver.find_element(By.XPATH, "//body").text

            error_reason = (
                "\nSeminar Workshop Faculty Update Verification Failed\n"
                "---------------------------------------------------\n"
                "Expected Result : Seminar row should show updated data after update.\n"
                "Actual Result   : Updated seminar row was not found in the table.\n\n"
                f"Old Title      : {TITLE}\n"
                f"Expected Title : {EDIT_TITLE}\n"
                f"Old Type       : {TYPE}\n"
                f"Expected Type  : {EDIT_TYPE}\n"
                f"Old Organizer  : {ORGANIZED_BY}\n"
                f"Expected Organizer : {EDIT_ORGANIZED_BY}\n"
                f"Old Achievement: {ACHIEVEMENT}\n"
                f"Expected Achievement : {EDIT_ACHIEVEMENT}\n\n"
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
                "Verify Seminar Workshop Faculty Updated",
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
        add_step(steps, driver, "Verify Seminar Workshop Faculty Deleted")

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
        create_pdf_report("Seminar_Workshop_Faculty_Test_Report", steps)