from pages.subject_group_page import SubjectGroupPage

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
SUBJECT_GROUP_URL = "https://devanttest.in/him_test/#/academics/subject-group"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

SUBJECT_GROUP_NAME = f"Test Subject Group {RANDOM_NUMBER}"
EDIT_SUBJECT_GROUP_NAME = f"Updated Subject Group {RANDOM_NUMBER}"


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

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact subject group row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def is_exact_table_row_present(driver, expected_values, timeout=5):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in expected_values):
                return True

        time.sleep(1)

    return False


def success_message_is_present(driver, expected_text, timeout=3):
    expected_text = expected_text.lower()
    end_time = time.time() + timeout

    while time.time() < end_time:
        body_text = driver.find_element(By.XPATH, "//body").text.lower()

        if expected_text in body_text:
            return True

        time.sleep(0.5)

    return False


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
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nSubject Group Delete Verification Failed\n"
        "----------------------------------------\n"
        "Expected Result : Updated subject group row should be deleted from the table.\n"
        "Actual Result   : Updated subject group row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_subject_group_form(page, subject_group_name):
    page.enter_subject_group_name(subject_group_name)
    selected_course, selected_semester = page.select_course_and_semester()
    selected_subject = page.select_subject()

    return selected_course, selected_semester, selected_subject


def test_subject_group_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SubjectGroupPage(driver)

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

        driver.get(SUBJECT_GROUP_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "subject-group" in driver.current_url.lower(), (
            f"Subject Group page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Subject Group Page")

        SELECTED_COURSE, SELECTED_SEMESTER, SELECTED_SUBJECT = fill_subject_group_form(
            page,
            SUBJECT_GROUP_NAME
        )
        add_step(steps, driver, "Fill Subject Group Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        EXPECTED_ROW_VALUES = [
            SUBJECT_GROUP_NAME,
            SELECTED_COURSE
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Subject Group Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_subject_group_name(EDIT_SUBJECT_GROUP_NAME)
        add_step(steps, driver, "Edit Subject Group Name")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        success_message_is_present(driver, "successfully updated")
        verify_no_validation_error(driver)

        driver.get(SUBJECT_GROUP_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        EDIT_EXPECTED_ROW_VALUES = [
            EDIT_SUBJECT_GROUP_NAME,
            SELECTED_COURSE
        ]

        if is_exact_table_row_present(driver, EDIT_EXPECTED_ROW_VALUES):
            DELETE_EXPECTED_ROW_VALUES = EDIT_EXPECTED_ROW_VALUES
        else:
            DELETE_EXPECTED_ROW_VALUES = EXPECTED_ROW_VALUES

        add_step(steps, driver, "Verify Subject Group Updated")

        page.click_delete_for_exact_row(
            DELETE_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            DELETE_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Subject Group Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Subject_Group_Test_Report", steps)
