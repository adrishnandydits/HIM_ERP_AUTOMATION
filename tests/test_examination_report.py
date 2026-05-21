from pages.examination_report_page import ExaminationReportPage

import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
EXAMINATION_REPORT_URL = "https://devanttest.in/him_test/#/report/examination-report"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA"
SEMESTER = "1st Sem"


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
            "//*[contains(normalize-space(),'EXAMINATION REPORT') or contains(normalize-space(),'STUDENT EXAMINATION REPORT')]"
        )

        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if any(element.is_displayed() for element in report_title) and len(rows) > 0:
            return True

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
                "Examination report data was not found. "
                "After clicking Search, the Examination Report table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Examination report was not loaded. "
        "After clicking Search, no report table row appeared. "
        "Please check whether the report API returned data for selected Course and Semester."
    )


def verify_report_title(driver):
    titles = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(),'EXAMINATION REPORT') or contains(normalize-space(),'STUDENT EXAMINATION REPORT')]"
    )

    visible_titles = [
        title.text.strip()
        for title in titles
        if title.is_displayed() and title.text.strip()
    ]

    assert len(visible_titles) > 0, "Examination Report title was not found."

    return True


def verify_report_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "course",
        "semester"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected examination report table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_report_table_has_rows(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Examination Report table has no rows. "
        "Please check selected Course and Semester."
    )

    return True


def verify_exact_table_row_found(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "Examination Report table body is empty."

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
        f"Exact examination report row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def fill_examination_report_filter(page):
    page.select_course()
    page.select_semester()


def test_examination_report_search_data_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ExaminationReportPage(driver)

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

        driver.get(EXAMINATION_REPORT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "examination-report" in driver.current_url.lower()

        add_step(steps, driver, "Open Examination Report Page")

        fill_examination_report_filter(page)
        add_step(steps, driver, "Fill Examination Report Filter")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_report_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Examination Report")


        verify_exact_table_row_found(
            driver,
            [COURSE, SEMESTER]
        )
        add_step(steps, driver, "Verify Examination Report Row")

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
        create_pdf_report("Examination_Report_Test_Report", steps)