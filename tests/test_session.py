from pages.session_page import SessionPage

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
SESSION_URL = "https://devanttest.in/him_test/#/academics/session"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(3000, 8999)

SESSION_NAME = str(RANDOM_NUMBER)
EDIT_SESSION_NAME = str(RANDOM_NUMBER + 1)


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS"):
    steps.append({
        "name": name,
        "status": status,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required')]"
    )

    visible_errors = [
        error.text for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def click_next_page_if_available(driver):
    next_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(),'Next')] | //a[contains(normalize-space(),'Next')]"
    )

    if not next_buttons:
        return False

    next_button = next_buttons[-1]
    button_class = next_button.get_attribute("class") or ""
    aria_disabled = next_button.get_attribute("aria-disabled") or ""
    disabled = next_button.get_attribute("disabled")

    if (
        disabled
        or aria_disabled.lower() == "true"
        or "disabled" in button_class.lower()
    ):
        return False

    try:
        next_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", next_button)

    time.sleep(1.5)
    return True


def table_has_exact_row(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        if all(value in row_text for value in expected_values):
            return True

    return False


def verify_exact_table_row_added(driver, expected_values):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + 30

    while time.time() < end_time:
        if table_has_exact_row(driver, expected_values):
            return True

        if not click_next_page_if_available(driver):
            time.sleep(1)

        else:
            continue

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact session row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values):
    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    end_time = time.time() + 30
    matching_row_text = ""

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        deleted_row_found = False

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in deleted_values):
                deleted_row_found = True
                matching_row_text = row.text
                break

        if not deleted_row_found:
            if not click_next_page_if_available(driver):
                return True
            continue

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nSession Delete Verification Failed\n"
        "----------------------------------\n"
        "Expected Result : Updated session row should be deleted from the table.\n"
        "Actual Result   : Updated session row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def test_session_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SessionPage(driver)

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

        driver.get(SESSION_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "session" in driver.current_url.lower(), (
            f"Session page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Session Page")

        page.enter_session(SESSION_NAME)
        add_step(steps, driver, "Enter Session")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [SESSION_NAME]
        )
        add_step(steps, driver, "Verify Session Added")

        page.click_edit_for_exact_row(
            [SESSION_NAME]
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_session(EDIT_SESSION_NAME)
        add_step(steps, driver, "Edit Session")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        verify_exact_table_row_added(
            driver,
            [EDIT_SESSION_NAME]
        )
        add_step(steps, driver, "Verify Session Updated")

        page.click_delete_for_exact_row(
            [EDIT_SESSION_NAME]
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [EDIT_SESSION_NAME]
        )
        add_step(steps, driver, "Verify Session Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Session_Test_Report", steps)
