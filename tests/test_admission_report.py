from pages.admission_report_page import AdmissionReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ADMISSION_REPORT_URL = "https://devanttest.in/him_test/#/report/admission-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

FROM_DATE = "2025-01-11"
TO_DATE = "2026-05-11"


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
        report_title = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'STUDENT ADMISSION REPORT')]"
        )

        if any(element.is_displayed() for element in report_title):
            return True

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
                "Admission report data was not found. "
                "After clicking Search, the Admission Report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Admission report was not loaded. "
        "After clicking Search, no report title or table row appeared. "
        "Please check whether the report API returned data for the selected date range."
    )


def verify_report_title(driver):
    titles = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(),'STUDENT ADMISSION REPORT')]"
    )

    visible_titles = [
        title.text.strip()
        for title in titles
        if title.is_displayed() and title.text.strip()
    ]

    assert len(visible_titles) > 0, "Student Admission Report title was not found."

    return True


def verify_report_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "gender",
        "date of birth",
        "user type",
        "mobile number",
        "email"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected report table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Admission report table has no rows. "
        "Please check selected From Date and To Date."
    )

    return True


def verify_report_date_range(driver, from_date, to_date):
    page_text = " ".join(driver.find_element(By.XPATH, "//body").text.split())

    assert "STUDENT ADMISSION REPORT" in page_text, (
        "Student Admission Report section was not found."
    )

    assert from_date in page_text or to_date in page_text, (
        f"Report date range not found on page. "
        f"Expected From Date: {from_date}, To Date: {to_date}. "
        f"Actual page text contains: {page_text[:500]}"
    )

    return True


def test_admission_report_search_data_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AdmissionReportPage(driver)

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

        driver.get(ADMISSION_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "admission-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Admission Report Page")

        page.click_data()
        add_step(steps, driver, "Click Data Button")

        page.enter_from_date(FROM_DATE)
        add_step(steps, driver, "Enter From Date")

        page.enter_to_date(TO_DATE)
        add_step(steps, driver, "Enter To Date")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Admission Report")

        #verify_report_title(driver)
        #add_step(steps, driver, "Verify Admission Report Title")

        verify_report_table_headers(driver)
        add_step(steps, driver, "Verify Admission Report Table Headers")

        verify_report_table_has_rows(driver)
        add_step(steps, driver, "Verify Admission Report Table Data")

        #verify_report_date_range(driver, FROM_DATE, TO_DATE)
        #add_step(steps, driver, "Verify Admission Report Date Range")

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
        create_pdf_report("Admission_Report_Test_Report", steps)