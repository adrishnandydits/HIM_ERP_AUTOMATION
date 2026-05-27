from pages.manual_scholarship_page import ManualScholarshipPage

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
MANUAL_SCHOLARSHIP_URL = "https://devanttest.in/him_test/#/fees-collection/manual-scholarship"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STUDENT_NAME = "MAINAK MONDAL"

RANDOM_NUMBER = random.randint(1000, 9999)

TYPE_OF_SCHOLARSHIP = "Concession"
AMOUNT = f"12{RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    screenshot_path = ""

    try:
        screenshot_path = take_screenshot(
            driver,
            name.lower().replace(" ", "_")
        )
    except Exception as screenshot_error:
        screenshot_path = ""

        screenshot_reason = (
            f"Screenshot failed: {type(screenshot_error).__name__}: {str(screenshot_error)}"
        )

        if reason:
            reason = f"{reason}\n{screenshot_reason}"
        else:
            reason = screenshot_reason

    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": screenshot_path
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
                f"Validation error found after save/search: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Manual scholarship record was not loaded. "
        "After clicking Save/Search, no row appeared in the Manual Scholarship table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


def fill_manual_scholarship_form(page):
    page.select_course_bba()
    page.select_semester_4th_sem()
    page.wait_for_student_options()
    page.select_student_by_name(STUDENT_NAME)
    page.enter_type_of_scholarship(TYPE_OF_SCHOLARSHIP)
    page.enter_amount(AMOUNT)


def search_manual_scholarship(page):
    page.select_show_course_bpharm()
    page.select_show_semester_4th_sem()
    page.select_show_student_by_name(STUDENT_NAME)
    page.click_search()


def test_manual_scholarship_add_show_search_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = ManualScholarshipPage(driver)

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

        driver.get(MANUAL_SCHOLARSHIP_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "manual-scholarship" in driver.current_url.lower(), (
            f"Manual Scholarship page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Manual Scholarship Page")

        try:
            fill_manual_scholarship_form(page)
            add_step(steps, driver, "Fill Manual Scholarship Form")

        except Exception as student_error:
            error_reason = str(student_error).strip()

            if not error_reason:
                error_reason = "Student selection failed, but Selenium did not return detailed reason."

            add_step(
                steps,
                driver,
                "Fill Manual Scholarship Form",
                "FAIL",
                reason=error_reason
            )

            raise AssertionError(error_reason)

        page.click_save()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Save Button")

        verify_no_validation_error(driver)

        page.click_show_manual_scholarship()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Manual Scholarship")

        try:
            search_manual_scholarship(page)
            wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
            add_step(steps, driver, "Search Manual Scholarship")

        except Exception as search_error:
            error_reason = str(search_error).strip()

            if not error_reason:
                error_reason = "Manual Scholarship search failed, but Selenium did not return detailed reason."

            add_step(
                steps,
                driver,
                "Search Manual Scholarship",
                "FAIL",
                reason=error_reason
            )

            raise AssertionError(error_reason)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Manual Scholarship List")

        page.verify_student_present_in_table(
            STUDENT_NAME,
            TYPE_OF_SCHOLARSHIP,
            AMOUNT
        )
        add_step(steps, driver, "Verify Manual Scholarship Added")

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
        create_pdf_report("Manual_Scholarship_Test_Report", steps)