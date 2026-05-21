from pages.apply_leave_page import ApplyLeavePage
from pages.approve_leave_page import ApproveLeavePage

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
APPLY_LEAVE_URL = "https://devanttest.in/him_test/#/human-resource/apply-leave"
APPROVE_LEAVE_URL = "https://devanttest.in/him_test/#/human-resource/approve-leave"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

MEMBER = "Arpita Das"
LEAVE_TYPE = "CL"

RANDOM_NUMBER = random.randint(1000, 9999)

FROM_DATE = "2026-05-10"
TO_DATE = "2026-05-11"

REASON = f"Approve leave reason {RANDOM_NUMBER}"


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

        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'No Data')]"
        )

        if any(element.is_displayed() for element in no_data):
            return False

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
                f"Validation error found: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Table data was not loaded. "
        "No row appeared and no validation message was found."
    )


def wait_for_no_data_or_empty_table(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'No Data')]"
        )

        if len(rows) == 0:
            return True

        if any(element.is_displayed() for element in no_data):
            return True

        time.sleep(1)

    raise AssertionError(
        "Pending leave was not removed after approval. "
        "Expected No Data or empty pending leave table."
    )


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No leave record found. Table body is empty."

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
        f"Exact leave row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_not_found(driver, deleted_values):
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
            f"Leave row still found. "
            f"Values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def fill_apply_leave_form(page):
    page.select_member()
    page.select_leave_type()
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(TO_DATE)
    page.enter_reason(REASON)


def test_apply_leave_approve_and_reject_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        apply_page = ApplyLeavePage(driver)

        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Login Page")

        apply_page.enter_text(apply_page.EMAIL, EMAIL)
        add_step(steps, driver, "Enter Email")

        apply_page.enter_text(apply_page.PASSWORD, PASSWORD)
        add_step(steps, driver, "Enter Password")

        apply_page.click(apply_page.LOGIN_BUTTON)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Login Button")

        driver.get(APPLY_LEAVE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "apply-leave" in driver.current_url.lower()

        add_step(steps, driver, "Open Apply Leave Page")

        fill_apply_leave_form(apply_page)
        add_step(steps, driver, "Fill Apply Leave Form")

        apply_page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Apply Leave Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Apply Leave List")

        verify_exact_table_row_added(
            driver,
            [MEMBER, LEAVE_TYPE]
        )
        add_step(steps, driver, "Verify Apply Leave Added")

        driver.get(APPROVE_LEAVE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "approve-leave" in driver.current_url.lower()

        approve_page = ApproveLeavePage(driver)

        add_step(steps, driver, "Open Approve Leave Page")

        approve_page.click_pending_leave_tab()
        add_step(steps, driver, "Click Pending Leave Tab")

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Pending Leave List")

        verify_exact_table_row_added(
            driver,
            [MEMBER, LEAVE_TYPE, FROM_DATE, TO_DATE]
        )
        add_step(steps, driver, "Verify Leave In Pending List")

        approve_page.click_approve()

        accept_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'Accept')]"
        )

        assert len(accept_buttons) > 0, (
            "Approve confirmation popup did not appear after clicking approve button."
        )

        add_step(steps, driver, "Click Approve Button")

        approve_page.confirm_approve()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Approve Leave")

        wait_for_no_data_or_empty_table(driver, timeout=25)
        add_step(steps, driver, "Verify Pending Leave Removed")

        approve_page.click_approved_leave_tab()
        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Click Approved Leave Tab")

        verify_exact_table_row_added(
            driver,
            [MEMBER, LEAVE_TYPE, FROM_DATE, TO_DATE, "Approved"]
        )
        add_step(steps, driver, "Verify Leave In Approved List")

        approve_page.click_reject()

        reject_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'Reject')]"
        )

        assert len(reject_buttons) > 0, (
            "Reject confirmation popup did not appear after clicking reject button."
        )

        add_step(steps, driver, "Click Reject Button From Approved Leave")
        time.sleep(7)

        approve_page.confirm_reject()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Reject Leave")

        approve_page.click_non_approved_leave_tab()
        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Click Non Approved Leave Tab")

        verify_exact_table_row_added(
            driver,
            [MEMBER, LEAVE_TYPE, FROM_DATE, TO_DATE, "Rejected"]
        )
        add_step(steps, driver, "Verify Leave In Non Approved List")

        approve_page.click_approved_leave_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Approved Leave Tab Again")

        verify_exact_table_row_not_found(
            driver,
            [MEMBER, LEAVE_TYPE, FROM_DATE, TO_DATE, "Approved"]
        )
        add_step(steps, driver, "Verify Leave Removed From Approved List")

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
        create_pdf_report("Approve_Leave_Test_Report", steps)