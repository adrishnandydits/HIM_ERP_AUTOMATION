from pages.staff_education_page import StaffEducationPage

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
STAFF_EDUCATION_URL = "https://devanttest.in/him_test/#/staff-information/staff-education"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"
DEGREE_NAME = "Msc"

RANDOM_NUMBER = random.randint(1000, 9999)

SPECIALIZATION = f"Test Specialization {RANDOM_NUMBER}"
UNIVERSITY_NAME = f"Test University {RANDOM_NUMBER}"
PERCENTAGE = "45"
GRADE = f"G{RANDOM_NUMBER}"

EDIT_SPECIALIZATION = f"Updated Specialization {RANDOM_NUMBER}"
EDIT_UNIVERSITY_NAME = f"Updated University {RANDOM_NUMBER}"
EDIT_PERCENTAGE = "55"
EDIT_GRADE = f"U{RANDOM_NUMBER}"

UPLOAD_FILE_PATH = r"C:\Users\Devant\Downloads\book_list (1).pdf"


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
        "//label[normalize-space()='File']/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Staff education file input was not found"

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
        "Staff education record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Staff Education table. "
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
        f"Exact staff education row not found after waiting 30 seconds. "
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
        "\nStaff Education Delete Verification Failed\n"
        "------------------------------------------\n"
        "Expected Result : Updated staff education row should be deleted from the table.\n"
        "Actual Result   : Updated staff education row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_staff_education_form(page):
    page.select_staff_shyam_samanta()
    page.select_degree_msc()
    page.enter_specialization(SPECIALIZATION)
    page.enter_university_name(UNIVERSITY_NAME)
    page.enter_percentage(PERCENTAGE)
    page.enter_grade(GRADE)
    page.upload_file(UPLOAD_FILE_PATH)


def fill_edit_staff_education_form(page):
    page.select_staff_shyam_samanta()
    page.select_degree_msc()
    page.enter_specialization(EDIT_SPECIALIZATION)
    page.enter_university_name(EDIT_UNIVERSITY_NAME)
    page.enter_percentage(EDIT_PERCENTAGE)
    page.enter_grade(EDIT_GRADE)
    page.upload_file(UPLOAD_FILE_PATH)


def test_staff_education_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = StaffEducationPage(driver)

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

        driver.get(STAFF_EDUCATION_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "staff-education" in driver.current_url.lower(), (
            f"Staff Education page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Staff Education Page")

        page.click_add_staff_education()
        add_step(steps, driver, "Click Add Staff Education")

        fill_staff_education_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Staff Education Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_staff_education()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Staff Education")

        try:
            page.search_staff_education(STAFF_NAME)
            wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
            add_step(steps, driver, "Search Staff Education")

        except Exception as search_error:
            error_reason = str(search_error).strip()

            if not error_reason:
                error_reason = "Staff Education search failed, but Selenium did not return detailed reason."

            add_step(
                steps,
                driver,
                "Search Staff Education",
                "FAIL",
                reason=error_reason
            )

            raise AssertionError(error_reason)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Staff Education List")

        EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            DEGREE_NAME,
            SPECIALIZATION,
            UNIVERSITY_NAME,
            PERCENTAGE,
            GRADE
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Staff Education Added")

        page.click_download_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download Staff Education File")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_staff_education_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Staff Education Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.click_show_staff_education()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Staff Education")

        try:
            page.search_staff_education(STAFF_NAME)
            wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
            add_step(steps, driver, "Search Updated Staff Education")

        except Exception as search_error:
            error_reason = str(search_error).strip()

            if not error_reason:
                error_reason = "Updated Staff Education search failed, but Selenium did not return detailed reason."

            add_step(
                steps,
                driver,
                "Search Updated Staff Education",
                "FAIL",
                reason=error_reason
            )

            raise AssertionError(error_reason)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Staff Education List")

        EDIT_EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            DEGREE_NAME,
            EDIT_SPECIALIZATION,
            EDIT_UNIVERSITY_NAME,
            EDIT_PERCENTAGE,
            EDIT_GRADE
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Staff Education Updated")

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
        add_step(steps, driver, "Verify Staff Education Deleted")

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
        create_pdf_report("Staff_Education_Test_Report", steps)