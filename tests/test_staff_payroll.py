from pages.staff_payroll_page import StaffPayrollPage

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
STAFF_PAYROLL_URL = "https://devanttest.in/him_test/#/human-resource/staff-payroll"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

USER_TYPE = "Students"
MONTH = "February"
YEAR = "2025"


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


def wait_for_payroll_table(driver, timeout=30):
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

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "Payroll search did not load any staff/student payroll record. "
        f"Actual page/table text: {table_text}"
    )


def verify_payroll_search_result(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "payroll" in page_text, (
        "Payroll page heading was not found after search."
    )

    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, (
        "Payroll table has no records after selecting "
        f"User Type: {USER_TYPE}, Month: {MONTH}, Year: {YEAR}."
    )

    return True


def verify_payroll_generated(driver):
    end_time = time.time() + 30

    while time.time() < end_time:
        page_text = " ".join(
            driver.find_element(By.XPATH, "//body").text.lower().split()
        )

        if (
            "revert" in page_text
            or "generated" in page_text
            or "payroll generated" in page_text
        ):
            return True

        time.sleep(1)

    page_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "Payroll generate verification failed. "
        "After clicking Generate Payroll, page did not show Revert/generated status. "
        f"Actual page text: {page_text}"
    )


def verify_payroll_reverted(driver):
    end_time = time.time() + 30

    while time.time() < end_time:
        page_text = " ".join(
            driver.find_element(By.XPATH, "//body").text.lower().split()
        )

        if "generate payroll" in page_text:
            return True

        time.sleep(1)

    page_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "Payroll revert verification failed. "
        "After clicking Revert, page did not show Generate Payroll again. "
        f"Actual page text: {page_text}"
    )


def test_staff_payroll_generate_revert_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = StaffPayrollPage(driver)

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

        driver.get(STAFF_PAYROLL_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "staff-payroll" in driver.current_url.lower(), (
            f"Staff Payroll page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Staff Payroll Page")

        page.select_user_type_students()
        add_step(steps, driver, "Select User Type")

        page.select_month_february()
        add_step(steps, driver, "Select Month")

        page.select_year_2025()
        add_step(steps, driver, "Select Year")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_payroll_table(driver, timeout=30)
        verify_payroll_search_result(driver)
        add_step(steps, driver, "Verify Payroll Search Result")

        page.click_generate_payroll_for_first_row()
        add_step(steps, driver, "Click Generate Payroll")

        page.confirm_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Generate Payroll")

        verify_payroll_generated(driver)
        add_step(steps, driver, "Verify Payroll Generated")

        page.click_revert_for_first_row()
        add_step(steps, driver, "Click Revert Payroll")

        page.confirm_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Revert Payroll")

        verify_payroll_reverted(driver)
        add_step(steps, driver, "Verify Payroll Reverted")

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
        create_pdf_report("Staff_Payroll_Test_Report", steps)