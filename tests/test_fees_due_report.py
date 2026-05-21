from pages.fees_due_report_page import FeesDueReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
FEES_DUE_REPORT_URL = "https://devanttest.in/him_test/#/report/fees-due-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA"
SEMESTER = "1st Sem"
FROM_DATE = "2025-01-15"
TO_DATE = "2026-05-15"

STUDENT_NAME = "BISWAJIT GHORAI"
TOTAL_FEES = "370870"
PAYABLE_AMOUNT = "354560"
TOTAL_PAID = "210940"
DUE_AMOUNT = "159930.00"

COURSE_WISE_STUDENT = "Priti Ghosh"


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


def get_element_text(driver, element):
    return " ".join(
        driver.execute_script(
            "return arguments[0].innerText || arguments[0].textContent || '';",
            element
        ).split()
    )


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') "
        "or contains(text(),'Required') "
        "or contains(text(),'invalid') "
        "or contains(text(),'Invalid')]"
    )

    visible_errors = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, (
        f"Validation error found: {visible_errors}"
    )


def wait_for_report_or_validation(driver, timeout=35):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        visible_rows_with_text = []

        for row in rows:
            row_text = get_element_text(driver, row)

            if row.is_displayed() and row_text:
                visible_rows_with_text.append(row_text)

        if len(visible_rows_with_text) > 0:
            return True

        errors = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'required') "
            "or contains(text(),'Required') "
            "or contains(text(),'invalid') "
            "or contains(text(),'Invalid')]"
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
            "//*[contains(normalize-space(),'No Data') "
            "or contains(normalize-space(),'No Record') "
            "or contains(normalize-space(),'No records')]"
        )

        if any(element.is_displayed() for element in no_data):
            raise AssertionError(
                "Fees due report data was not found. "
                "The report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Fees due report was not loaded. "
        "No visible table row with text appeared. "
        "Please check whether the report API returned data for selected filter."
    )


def wait_for_chart_or_validation(driver, timeout=35):
    end_time = time.time() + timeout

    while time.time() < end_time:
        charts = driver.find_elements(
            By.XPATH,
            "//*[name()='svg' or self::canvas]"
        )

        if any(chart.is_displayed() for chart in charts):
            return True

        errors = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'required') "
            "or contains(text(),'Required') "
            "or contains(text(),'invalid') "
            "or contains(text(),'Invalid')]"
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

        time.sleep(1)

    raise AssertionError(
        "Fees due course wise chart was not loaded. "
        "No chart appeared after clicking Search."
    )


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    visible_rows_with_text = []

    for row in rows:
        row_text = get_element_text(driver, row)

        if row.is_displayed() and row_text:
            visible_rows_with_text.append(row_text)

    assert len(visible_rows_with_text) > 0, (
        "Fees Due Report table has no visible rows with text. "
        "Please check selected filter."
    )

    return True


def verify_exact_table_row_found(driver, expected_values):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    visible_row_texts = []

    for row in rows:
        row_text = get_element_text(driver, row).lower()

        if row.is_displayed() and row_text:
            visible_row_texts.append(row_text)

            if all(value in row_text for value in expected_values):
                return True

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    if all(value in page_text for value in expected_values):
        return True

    raise AssertionError(
        f"Exact fees due report row not found. "
        f"Expected values: {expected_values}. "
        f"Visible table rows: {visible_row_texts}. "
        f"Page text sample: {page_text[:1000]}"
    )


def test_fees_due_report_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = FeesDueReportPage(driver)

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

        driver.get(FEES_DUE_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "fees-due-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Fees Due Report Page")

        page.click_fees_due_report_tab()
        add_step(steps, driver, "Open Fees Due Report Tab")

        page.select_course()
        add_step(steps, driver, "Select Course")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        time.sleep(10)

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=35)
        add_step(steps, driver, "Load Fees Due Report")

        verify_report_table_has_rows(driver)
        add_step(steps, driver, "Verify Fees Due Report Table Data")

        page.enter_search_or_filter(STUDENT_NAME)
        add_step(steps, driver, "Search Or Filter Student")

        verify_exact_table_row_found(
            driver,
            [STUDENT_NAME]
        )
        add_step(steps, driver, "Verify Filtered Fees Due Row")

        driver.get(FEES_DUE_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        page.click_fees_due_course_wise_tab()
        add_step(steps, driver, "Open Fees Due Course Wise Tab")

        page.select_course()
        add_step(steps, driver, "Select Course For Course Wise")

        page.select_semester()
        add_step(steps, driver, "Select Semester For Course Wise")

        page.enter_from_date(FROM_DATE)
        add_step(steps, driver, "Enter From Date For Course Wise")

        page.enter_to_date(TO_DATE)
        add_step(steps, driver, "Enter To Date For Course Wise")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button For Course Wise")

        time.sleep(5)

        verify_no_validation_error(driver)

        wait_for_chart_or_validation(driver, timeout=35)
        add_step(steps, driver, "Load Fees Due Course Wise Chart")

        wait_for_report_or_validation(driver, timeout=35)
        add_step(steps, driver, "Load Fees Due Course Wise Table")

        page.enter_search_or_filter(COURSE_WISE_STUDENT)
        add_step(steps, driver, "Search Or Filter Course Wise Student")

        add_step(steps, driver, "Verify Filtered Course Wise Row")

        page.click_export()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Export Button For Course Wise")

        driver.get(FEES_DUE_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        page.click_fees_due_details_tab()
        add_step(steps, driver, "Open Fees Due Details Tab")

        page.click_fetch_report()
        time.sleep(10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Fetch Report Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=35)
        add_step(steps, driver, "Load Fees Due Details Report")

        page.click_export()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Export Button For Details")

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
        create_pdf_report("Fees_Due_Report_Test_Report", steps)