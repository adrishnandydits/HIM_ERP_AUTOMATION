from pages.attendance_report_page import AttendanceReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ATTENDANCE_REPORT_URL = "https://devanttest.in/him_test/#/report/attendance-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA"
SEMESTER = "1st Sem"
FROM_DATE = "2026-01-01"
TO_DATE = "2026-05-11"
NAME = "dasdas dasd asdas"
PRESENT = 0
ABSENT = 0

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


def wait_for_report_or_validation(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
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
                "Attendance report data was not found. "
                "After clicking Search, the Attendance Report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Attendance report was not loaded. "
        "After clicking Search, no table row appeared. "
        "Please check whether the report API returned data for the selected "
        "Course, Semester, From Date and To Date."
    )


def verify_report_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "course",
        "sem"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected attendance report table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Attendance report table has no rows. "
        "Please check selected Course, Semester, From Date and To Date."
    )

    return True


def verify_table_contains_values(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "Attendance report table body is empty."

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    table_text = " ".join(
        driver.find_element(By.XPATH, "//table//tbody").text.lower().split()
    )

    for value in expected_values:
        assert value.lower() in table_text, (
            f"Expected value not found in attendance report table: {value}. "
            f"Actual table text: {table_text}"
        )

    return True


def fill_attendance_report_filter(page):
    page.select_course(COURSE)
    page.select_semester(SEMESTER)
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)


def test_attendance_report_search_data_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AttendanceReportPage(driver)

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

        driver.get(ATTENDANCE_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "attendance-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Attendance Report Page")

        fill_attendance_report_filter(page)
        add_step(steps, driver, "Fill Attendance Report Filter")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Attendance Report")

        verify_table_contains_values(
            driver,
            [
                NAME
            ]
        )
        add_step(steps, driver, "Verify Attendance Report Selected Data")

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
        create_pdf_report("Attendance_Report_Test_Report", steps)