from pages.fees_type_page import FeesTypePage

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
FEES_TYPE_URL = "https://devanttest.in/him_test/#/fees-collection/fees-type"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

FEES_TYPE_NAME = f"Test Fees Type {RANDOM_NUMBER}"
EDIT_FEES_TYPE_NAME = f"Updated Fees Type {RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    image_path = ""

    try:
        image_path = take_screenshot(
            driver,
            name.lower().replace(" ", "_")
        )
    except Exception:
        image_path = ""

    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": image_path
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
    )

    visible_errors = []

    for error in errors:
        try:
            if error.is_displayed() and error.text.strip():
                visible_errors.append(error.text.strip())
        except StaleElementReferenceException:
            continue

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_table_or_validation(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            errors = driver.find_elements(
                By.XPATH,
                "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
            )

            visible_errors = []

            for error in errors:
                try:
                    if error.is_displayed() and error.text.strip():
                        visible_errors.append(error.text.strip())
                except StaleElementReferenceException:
                    continue

            if visible_errors:
                raise AssertionError(
                    f"Validation error found after submit/update: {visible_errors}"
                )

            no_data_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no records')]"
            )

            visible_no_data = []

            for element in no_data_elements:
                try:
                    if element.is_displayed() and element.text.strip():
                        visible_no_data.append(element.text.strip())
                except StaleElementReferenceException:
                    continue

            if visible_no_data:
                raise AssertionError(
                    f"No fees type data found. Message shown: {visible_no_data}"
                )

            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                try:
                    if row.is_displayed() and row.text.strip():
                        return True
                except StaleElementReferenceException:
                    continue

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError(
        "Fees Type table was not loaded. "
        "After clicking Submit/Update, no stable row appeared."
    )


def verify_exact_table_row_added(driver, expected_values, timeout=25):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in expected_values):
                    return True

        except StaleElementReferenceException:
            time.sleep(1)

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Exact fees type row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table/body text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values, timeout=25):
    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            if len(rows) == 0:
                return True

            deleted_row_found = False

            for row in rows:
                try:
                    row_text = " ".join(row.text.lower().split())

                    if all(value in row_text for value in deleted_values):
                        deleted_row_found = True
                        break
                except StaleElementReferenceException:
                    continue

            if not deleted_row_found:
                return True

        except StaleElementReferenceException:
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = ""

    raise AssertionError(
        f"Deleted fees type row still found after waiting. "
        f"Deleted values: {deleted_values}. "
        f"Actual table text: {table_text}"
    )


def verify_fees_type_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "fees type" in page_text, (
        "Fees Type page heading was not found."
    )

    assert "add fees type" in page_text, (
        "Add Fees Type section was not found."
    )

    assert "fees type name" in page_text, (
        "Fees Type Name field was not found."
    )

    assert "fees type list" in page_text, (
        "Fees Type List section was not found."
    )

    assert "submit" in page_text, (
        "Submit button was not found."
    )

    return True


def verify_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "fees type name",
        "action"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected Fees Type table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def fill_fees_type_form(page, fees_type_name):
    page.scroll_page_top()
    page.enter_fees_type_name(fees_type_name)


def test_fees_type_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = FeesTypePage(driver)

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

        driver.get(FEES_TYPE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "fees-type" in driver.current_url.lower()

        add_step(steps, driver, "Open Fees Type Page")

        verify_fees_type_page(driver)
        add_step(steps, driver, "Verify Fees Type Page")

        fill_fees_type_form(page, FEES_TYPE_NAME)
        add_step(steps, driver, "Fill Fees Type Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Fees Type List")

        verify_table_headers(driver)
        add_step(steps, driver, "Verify Fees Type Table Headers")

        ADDED_ROW_VALUES = [
            FEES_TYPE_NAME
        ]

        verify_exact_table_row_added(
            driver,
            ADDED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Fees Type Added")

        page.click_edit_for_exact_row([FEES_TYPE_NAME])
        wait.until(EC.presence_of_element_located(page.FEES_TYPE_NAME))
        add_step(steps, driver, "Click Edit Button For Exact Added Fees Type")

        fill_fees_type_form(page, EDIT_FEES_TYPE_NAME)
        add_step(steps, driver, "Edit Fees Type Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Fees Type List")

        UPDATED_ROW_VALUES = [
            EDIT_FEES_TYPE_NAME
        ]

        verify_exact_table_row_added(
            driver,
            UPDATED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Fees Type Updated")

        page.click_delete_for_exact_row([EDIT_FEES_TYPE_NAME])

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
            "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(steps, driver, "Click Delete Button For Exact Updated Fees Type")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(2)
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [EDIT_FEES_TYPE_NAME],
            timeout=25
        )
        add_step(steps, driver, "Verify Fees Type Deleted")

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
        create_pdf_report("Fees_Type_Test_Report", steps)