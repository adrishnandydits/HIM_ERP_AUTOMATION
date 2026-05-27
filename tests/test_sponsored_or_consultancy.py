from pages.sponsored_or_consultancy_page import SponsoredOrConsultancyPage

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
SPONSORED_OR_CONSULTANCY_URL = "https://devanttest.in/him_test/#/staff-information/sponsored-or-consultancy"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"

RANDOM_NUMBER = random.randint(1000, 9999)

PROJECT_CONSULTANCY = f"Test Project {RANDOM_NUMBER}"
SPONSORED_BY = f"Test Sponsor {RANDOM_NUMBER}"
CONSULTANT = f"Test Consultant {RANDOM_NUMBER}"
AMOUNT = f"32{RANDOM_NUMBER}"
DURATION = f"3{random.randint(1, 9)}"
STATUS = "Ongoing"
TABLE_STATUS = "ongoing"

EDIT_PROJECT_CONSULTANCY = f"Updated Project {RANDOM_NUMBER}"
EDIT_SPONSORED_BY = f"Updated Sponsor {RANDOM_NUMBER}"
EDIT_CONSULTANT = f"Updated Consultant {RANDOM_NUMBER}"
EDIT_AMOUNT = f"42{RANDOM_NUMBER}"
EDIT_DURATION = f"4{random.randint(1, 9)}"
EDIT_STATUS = "Ongoing"
EDIT_TABLE_STATUS = "ongoing"


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
        "Sponsored Project/Consultancy record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Sponsored Project/Consultancy table. "
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
        f"Exact sponsored project consultancy row not found after waiting 30 seconds. "
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
        "\nSponsored Project/Consultancy Delete Verification Failed\n"
        "--------------------------------------------------------\n"
        "Expected Result : Updated sponsored project consultancy row should be deleted from the table.\n"
        "Actual Result   : Updated sponsored project consultancy row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_sponsored_project_consultancy_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_project_consultancy(PROJECT_CONSULTANCY)
    page.enter_sponsored_by(SPONSORED_BY)
    page.enter_consultant(CONSULTANT)
    page.enter_amount(AMOUNT)
    page.enter_duration(DURATION)
    page.select_status_ongoing()


def fill_edit_sponsored_project_consultancy_form(page):
    page.select_staff_by_name(STAFF_NAME)
    page.enter_project_consultancy(EDIT_PROJECT_CONSULTANCY)
    page.enter_sponsored_by(EDIT_SPONSORED_BY)
    page.enter_consultant(EDIT_CONSULTANT)
    page.enter_amount(EDIT_AMOUNT)
    page.enter_duration(EDIT_DURATION)
    page.select_status_ongoing()


def test_sponsored_or_consultancy_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SponsoredOrConsultancyPage(driver)

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

        driver.get(SPONSORED_OR_CONSULTANCY_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "sponsored-or-consultancy" in driver.current_url.lower(), (
            f"Sponsored Project/Consultancy page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Sponsored Project Consultancy Page")

        page.click_add_sponsored_project_consultancy()
        add_step(steps, driver, "Click Add Sponsored Project Consultancy")

        fill_sponsored_project_consultancy_form(page)
        add_step(steps, driver, "Fill Sponsored Project Consultancy Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        page.click_show_sponsored_project_consultancy()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Sponsored Project Consultancy")

        page.search_sponsored_project_consultancy(STAFF_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Sponsored Project Consultancy")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Sponsored Project Consultancy List")

        EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            PROJECT_CONSULTANCY,
            SPONSORED_BY,
            CONSULTANT,
            AMOUNT,
            DURATION,
            TABLE_STATUS
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Sponsored Project Consultancy Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_sponsored_project_consultancy_form(page)
        add_step(steps, driver, "Edit Sponsored Project Consultancy Form")

        page.click_update()
        page.confirm_update_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        page.click_show_sponsored_project_consultancy()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Sponsored Project Consultancy")

        page.search_sponsored_project_consultancy(STAFF_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Sponsored Project Consultancy")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Sponsored Project Consultancy List")

        EDIT_EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            EDIT_PROJECT_CONSULTANCY,
            EDIT_SPONSORED_BY,
            EDIT_CONSULTANT,
            EDIT_AMOUNT,
            EDIT_DURATION,
            EDIT_TABLE_STATUS
        ]

        try:
            verify_exact_table_row_added(
                driver,
                EDIT_EXPECTED_ROW_VALUES
            )
            add_step(steps, driver, "Verify Sponsored Project Consultancy Updated")

        except Exception as update_verify_error:
            table_text = ""

            try:
                table_text = driver.find_element(By.XPATH, "//table//tbody").text
            except Exception:
                table_text = driver.find_element(By.XPATH, "//body").text

            error_reason = (
                "\nSponsored Project/Consultancy Update Verification Failed\n"
                "--------------------------------------------------------\n"
                "Expected Result : Sponsored project consultancy row should show updated data after update.\n"
                "Actual Result   : Updated sponsored project consultancy row was not found in the table.\n\n"
                f"Old Project Consultancy      : {PROJECT_CONSULTANCY}\n"
                f"Expected Project Consultancy : {EDIT_PROJECT_CONSULTANCY}\n"
                f"Old Sponsored By             : {SPONSORED_BY}\n"
                f"Expected Sponsored By        : {EDIT_SPONSORED_BY}\n"
                f"Old Consultant               : {CONSULTANT}\n"
                f"Expected Consultant          : {EDIT_CONSULTANT}\n"
                f"Old Amount                   : {AMOUNT}\n"
                f"Expected Amount              : {EDIT_AMOUNT}\n"
                f"Old Duration                 : {DURATION}\n"
                f"Expected Duration            : {EDIT_DURATION}\n\n"
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
                "Verify Sponsored Project Consultancy Updated",
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
        add_step(steps, driver, "Verify Sponsored Project Consultancy Deleted")

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
        create_pdf_report("Sponsored_Project_Consultancy_Test_Report", steps)