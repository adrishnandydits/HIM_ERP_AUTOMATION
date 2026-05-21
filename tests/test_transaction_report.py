from pages.transaction_report_page import TransactionReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
TRANSACTION_REPORT_URL = "https://devanttest.in/him_test/#/report/transaction-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

FILTER_BY = "Paid On"
FROM_DATE = "2026-01-01"
TO_DATE = "2026-05-11"
MODE = "All"
STUDENT = "SAROJ PRADHAN"


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


def wait_for_report_or_validation(driver, timeout=25):
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
                f"Validation error found after search: {visible_errors}"
            )

        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'No Data') or contains(normalize-space(),'No Record') or contains(normalize-space(),'No records')]"
        )

        if any(element.is_displayed() for element in no_data):
            raise AssertionError(
                "Transaction report data was not found. "
                "After clicking Search, the Transaction Report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Transaction report was not loaded. "
        "After clicking Search, no table row appeared. "
        "Please check whether the report API returned data for the selected filter."
    )


def verify_report_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "received date",
        "name",
        "course",
        "sem",
        "session",
        "id",
        "registration fees",
        "exam fees",
        "admission fees",
        "tuition fees"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected transaction report table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Transaction report table has no rows. "
        "Please check selected From Date, To Date, Mode and Student."
    )

    return True


def verify_exact_table_row_found(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "Transaction report table body is empty."

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
        f"Exact transaction report row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def fill_transaction_report_filter(page):
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.select_student()


def test_transaction_report_search_data_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = TransactionReportPage(driver)

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

        driver.get(TRANSACTION_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "transaction-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Transaction Report Page")

        fill_transaction_report_filter(page)
        add_step(steps, driver, "Fill Transaction Report Filter")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Transaction Report")


        verify_report_table_has_rows(driver)
        add_step(steps, driver, "Verify Transaction Report Table Data")

        verify_exact_table_row_found(
            driver,
            [STUDENT]
        )
        add_step(steps, driver, "Verify Student Transaction Row")

        page.enter_search_or_filter(STUDENT)
        add_step(steps, driver, "Search Or Filter Student")

        verify_exact_table_row_found(
            driver,
            [STUDENT]
        )
        add_step(steps, driver, "Verify Filtered Transaction Row")

        page.click_export()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Export Button")

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
        create_pdf_report("Transaction_Report_Test_Report", steps)