from pages.certificate_types_page import CertificateTypesPage

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
CERTIFICATE_TYPES_URL = "https://devanttest.in/him_test/#/student-information/certificate-types"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

CERTIFICATE_TYPE_NAME = f"Test Certificate Type {RANDOM_NUMBER}"
EDIT_CERTIFICATE_TYPE_NAME = f"Updated Certificate Type {RANDOM_NUMBER}"


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

    visible_errors = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_table_or_validation(driver, timeout=25):
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

        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'No Data') or contains(normalize-space(),'No Record') or contains(normalize-space(),'No records')]"
        )

        if any(element.is_displayed() for element in no_data):
            raise AssertionError(
                "Certificate type record was not added. "
                "After clicking Submit, the Certificate Type List table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Certificate type record was not added. "
        "After clicking Submit, no row appeared in the Certificate Type List table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No certificate type record added. Table body is empty."

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        if all(value in row_text for value in expected_values):
            return True

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact certificate type row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
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
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in deleted_values):
                    deleted_row_found = True
                    break

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
        f"Deleted certificate type row still found after waiting. "
        f"Deleted values: {deleted_values}. "
        f"Actual table text: {table_text}"
    )


def fill_certificate_type_form(page, certificate_type_name):
    page.enter_certificate_type_name(certificate_type_name)


def test_certificate_types_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = CertificateTypesPage(driver)

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

        driver.get(CERTIFICATE_TYPES_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "certificate-types" in driver.current_url.lower()

        add_step(steps, driver, "Open Certificate Types Page")

        fill_certificate_type_form(
            page,
            CERTIFICATE_TYPE_NAME
        )
        add_step(steps, driver, "Fill Certificate Type Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Certificate Type List")

        ADDED_ROW_VALUES = [
            CERTIFICATE_TYPE_NAME
        ]

        verify_exact_table_row_added(
            driver,
            ADDED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Certificate Type Added")

        page.click_edit_for_exact_row(ADDED_ROW_VALUES)
        wait.until(EC.presence_of_element_located(page.CERTIFICATE_TYPE_NAME))
        add_step(steps, driver, "Click Edit Button For Exact Added Row")

        page.enter_certificate_type_name(EDIT_CERTIFICATE_TYPE_NAME)
        add_step(steps, driver, "Edit Certificate Type Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Certificate Type List")

        UPDATED_ROW_VALUES = [
            EDIT_CERTIFICATE_TYPE_NAME
        ]

        verify_exact_table_row_added(
            driver,
            UPDATED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Certificate Type Updated")

        page.click_delete_for_exact_row(UPDATED_ROW_VALUES)

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(steps, driver, "Click Delete Button For Exact Added Row")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(2)
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            UPDATED_ROW_VALUES,
            timeout=25
        )
        add_step(steps, driver, "Verify Certificate Type Deleted")

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
        create_pdf_report("Certificate_Types_Test_Report", steps)