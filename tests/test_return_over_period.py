from pages.return_over_period_page import ReturnOverPeriodPage

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
RETURN_OVER_PERIOD_URL = "https://devanttest.in/him_test/#/library/return-over-period"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

SEARCH_TEXT = "Test Book"


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


def verify_return_over_period_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "return over period" in page_text, (
        "Return Over Period page heading was not found."
    )

    assert "search" in page_text, (
        "Search section was not found on Return Over Period page."
    )

    assert "user name" in page_text, (
        "User Name table column was not found."
    )

    assert "book name" in page_text, (
        "Book Name table column was not found."
    )

    assert "publisher" in page_text, (
        "Publisher table column was not found."
    )

    assert "author" in page_text, (
        "Author table column was not found."
    )

    assert "issued on" in page_text, (
        "Issued On table column was not found."
    )

    assert "return date" in page_text, (
        "Return Date table column was not found."
    )

    assert "late fine" in page_text, (
        "Late Fine table column was not found."
    )

    assert "discount" in page_text, (
        "Discount table column was not found."
    )

    assert "total fine" in page_text, (
        "Total Fine table column was not found."
    )

    return True


def verify_row_exists(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    if len(rows) > 0:
        return True

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nReturn Over Period Row Verification Failed\n"
        "------------------------------------------\n"
        "Expected Result : At least one row should be present in the Return Over Period table.\n"
        "Actual Result   : No rows are present in the Return Over Period table.\n\n"
        "Possible Reason :\n"
        "1. No book return is currently over period.\n"
        "2. Return Over Period data was not generated.\n"
        "3. Table data API returned empty response.\n"
        "4. Page loaded successfully, but no matching records exist.\n\n"
        f"Actual Table/Page Text:\n{table_text}"
    )


def verify_search_result_exists(driver, search_text):
    search_text = str(search_text).lower().strip()

    end_time = time.time() + 15

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) == 0:
            break

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if search_text in row_text:
                return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nReturn Over Period Search Verification Failed\n"
        "---------------------------------------------\n"
        f"Expected Result : Search result should contain '{search_text}'.\n"
        "Actual Result   : Search result was not found in the table.\n\n"
        f"Actual Table/Page Text:\n{table_text}"
    )


def test_return_over_period_row_exists_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ReturnOverPeriodPage(driver)

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

        driver.get(RETURN_OVER_PERIOD_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "return-over-period" in driver.current_url.lower(), (
            f"Return Over Period page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Return Over Period Page")

        verify_return_over_period_page(driver)
        page.verify_table_headers()
        add_step(steps, driver, "Verify Return Over Period Table Headers")

        verify_row_exists(driver)
        add_step(steps, driver, "Verify Return Over Period Row Exists")

        page.search_return_over_period(SEARCH_TEXT)
        add_step(steps, driver, "Search Return Over Period")

        verify_search_result_exists(
            driver,
            SEARCH_TEXT
        )
        add_step(steps, driver, "Verify Search Result Exists")

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
        create_pdf_report("Return_Over_Period_Test_Report", steps)