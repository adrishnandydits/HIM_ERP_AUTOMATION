from pages.scholarship_report_page import ScholarshipReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/hlc_test/#/auth/login"
SCHOLARSHIP_REPORT_URL = "https://devanttest.in/hlc_test/#/report/scholarship-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

FROM_DATE = "2026-02-01"
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
                "Scholarship report data was not found. "
                "After clicking Search, the Scholarship Report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Scholarship report was not loaded. "
        "After clicking Search, no table row appeared. "
        "Please check whether the report API returned data for the selected dates."
    )


def verify_report_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "course",
        "sem",
        "session",
        "scholarship"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected scholarship report table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Scholarship report table has no rows. "
        "Please check selected From Date and To Date."
    )

    return True


def fill_scholarship_report_filter(page):
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)


def test_scholarship_report_search_data_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ScholarshipReportPage(driver)

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

        driver.get(SCHOLARSHIP_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "scholarship-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Scholarship Report Page")

        fill_scholarship_report_filter(page)
        add_step(steps, driver, "Fill Scholarship Report Filter")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Scholarship Report")

        verify_report_table_has_rows(driver)
        add_step(steps, driver, "Verify Scholarship Report Table Data")

        page.click_clear()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Clear Button")

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
        create_pdf_report("Scholarship_Report_Test_Report", steps)