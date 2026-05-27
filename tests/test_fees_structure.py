from pages.fees_structure_page import FeesStructurePage

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
FEES_STRUCTURE_URL = "https://devanttest.in/him_test/#/fees-collection/fees-structure"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE_NAME = "BBA (Hospital Management)"
SEMESTER_NAME = "2nd Sem"
FEES_TYPE_NAME = "Admission fees"

RANDOM_NUMBER = random.randint(1000, 9999)

LAST_DATE = "23-05-2026"
TABLE_LAST_DATE = "2026-05-23"
AMOUNT = f"54{RANDOM_NUMBER}"


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
                f"Validation error found after add/save/search: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Fees structure record was not loaded. "
        "After clicking Add/Save/Search, no row appeared in the Fees Structure table. "
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
        f"Exact fees structure row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table/page text: {table_text}"
    )


def fill_fees_structure_form(page):
    page.select_course_bba()
    page.select_semester_2nd_sem()
    page.enter_last_date(LAST_DATE)
    page.select_fees_type_admission_fees()
    page.enter_amount(AMOUNT)


def test_fees_structure_add_save_show_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = FeesStructurePage(driver)

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

        driver.get(FEES_STRUCTURE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "fees-structure" in driver.current_url.lower(), (
            f"Fees Structure page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Fees Structure Page")

        fill_fees_structure_form(page)
        add_step(steps, driver, "Fill Fees Structure Form")

        page.click_add()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Add Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Fees Structure Temporary List")

        TEMP_EXPECTED_ROW_VALUES = [
            SEMESTER_NAME,
            FEES_TYPE_NAME,
            AMOUNT
        ]

        verify_exact_table_row_added(
            driver,
            TEMP_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Fees Structure Added In Temporary List")

        page.click_save()
        page.confirm_save_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Save Button")

        verify_no_validation_error(driver)

        page.search_fees_structure()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Fees Structure")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Saved Fees Structure List")

        SAVED_EXPECTED_ROW_VALUES = [
            SEMESTER_NAME,
            TABLE_LAST_DATE,
            FEES_TYPE_NAME,
            AMOUNT
        ]

        verify_exact_table_row_added(
            driver,
            SAVED_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Fees Structure Saved")

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
        create_pdf_report("Fees_Structure_Test_Report", steps)