from pages.holiday_page import HolidayPage

import pytest
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
HOLIDAY_URL = "https://devanttest.in/him_test/#/human-resource/holiday"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

HOLIDAY_DATE = "2026-01-04"
HOLIDAY_DESCRIPTION = f"Test Holiday {RANDOM_NUMBER}"
EDIT_HOLIDAY_DESCRIPTION = f"Updated Holiday {RANDOM_NUMBER}"

MONTH = "January"


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


def wait_for_table_or_validation(driver, timeout=25):
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

    raise AssertionError(
        "Holiday record was not loaded. "
        "No row appeared in the Holiday List table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No holiday record added. Table body is empty."

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
        f"Exact holiday row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    if len(rows) == 0:
        return True

    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        assert not all(value in row_text for value in deleted_values), (
            f"Deleted holiday row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def test_holiday_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = HolidayPage(driver)

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

        driver.get(HOLIDAY_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "holiday" in driver.current_url.lower()

        add_step(steps, driver, "Open Holiday Page")

        page.enter_holiday_date(HOLIDAY_DATE)
        add_step(steps, driver, "Enter Holiday Date")

        page.enter_description(HOLIDAY_DESCRIPTION)
        add_step(steps, driver, "Enter Holiday Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.select_month()
        add_step(steps, driver, "Select Month")

        page.click_month_submit()
        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Holiday List")

        verify_exact_table_row_added(
            driver,
            [HOLIDAY_DATE, HOLIDAY_DESCRIPTION]
        )
        add_step(steps, driver, "Verify Holiday Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.DESCRIPTION))
        add_step(steps, driver, "Click Edit Button")

        page.enter_description(EDIT_HOLIDAY_DESCRIPTION)
        add_step(steps, driver, "Edit Holiday Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.select_month()
        add_step(steps, driver, "Select Month After Update")

        page.click_month_submit()
        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Holiday List")

        verify_exact_table_row_added(
            driver,
            [HOLIDAY_DATE, EDIT_HOLIDAY_DESCRIPTION]
        )
        add_step(steps, driver, "Verify Holiday Updated")

        page.click_delete()

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        add_step(steps, driver, "Click Delete Button")

        verify_exact_table_row_deleted(
            driver,
            [HOLIDAY_DATE, EDIT_HOLIDAY_DESCRIPTION]
        )
        add_step(steps, driver, "Verify Holiday Deleted")

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
        create_pdf_report("Holiday_Test_Report", steps)