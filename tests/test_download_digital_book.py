from pages.download_digital_book_page import DownloadDigitalBookPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
DOWNLOAD_DIGITAL_BOOK_URL = "https://devanttest.in/him_test/#/library/download-digital-book"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE_TEXT = "BBA (Hospital Management)"
SEMESTER_TEXT = "2nd Sem"
BOOK_NAME = "Test Book"
PDF_NAME = "book_list (1).pdf"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
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
                f"Validation error found after submit: {visible_errors}"
            )

        time.sleep(1)

    page_text = ""

    try:
        page_text = driver.find_element(By.XPATH, "//body").text
    except Exception:
        page_text = "Unable to read page text."

    raise AssertionError(
        "Download digital book table was not loaded. "
        "After clicking Submit, no row appeared in the Download Digital Books table. "
        f"Actual page text: {page_text}"
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
        f"Exact download digital book row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table/page text: {table_text}"
    )


def verify_download_digital_book_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "download digital books" in page_text, (
        "Download Digital Books page heading was not found."
    )

    assert "select course" in page_text, (
        "Select Course field was not found."
    )

    assert "select semester" in page_text, (
        "Select Semester field was not found."
    )

    assert "submit" in page_text, (
        "Submit button was not found."
    )

    return True


def test_download_digital_book_search_download_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = DownloadDigitalBookPage(driver)

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

        driver.get(DOWNLOAD_DIGITAL_BOOK_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "download-digital-book" in driver.current_url.lower(), (
            f"Download Digital Book page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Download Digital Book Page")

        verify_download_digital_book_page(driver)
        add_step(steps, driver, "Verify Download Digital Book Page")

        page.select_course_bba_hospital_management()
        add_step(steps, driver, "Select Course")

        page.select_semester_2nd_sem()
        add_step(steps, driver, "Select Semester")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Download Digital Books List")

        EXPECTED_ROW_VALUES = [
            COURSE_TEXT,
            SEMESTER_TEXT,
            BOOK_NAME,
            PDF_NAME
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Download Digital Book Row")

        page.click_download_link_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download PDF Link")

        verify_no_validation_error(driver)

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
        create_pdf_report("Download_Digital_Book_Test_Report", steps)