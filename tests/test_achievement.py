from pages.achievement_page import AchievementPage

import os
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
ACHIEVEMENT_URL = "https://devanttest.in/him_test/#/student-information/achievement"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

COURSE = "BBA (Hospital Management)"
SEMESTER = "2nd Sem"
ACHIEVEMENT_DATE = "2026-05-11"

AWARD_NAME = f"Test Award {RANDOM_NUMBER}"
EDIT_AWARD_NAME = f"Updated Award {RANDOM_NUMBER}"

UPLOAD_FILE_PATH = r"C:\Users\LENOVO\Downloads\Test.png"


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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "No achievement upload file input found"

    uploaded_file_value = file_inputs[0].get_attribute("value")

    assert uploaded_file_value != "", "Achievement file was not uploaded"

    return True


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

        no_data = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(),'No Data') or contains(normalize-space(),'No Record') or contains(normalize-space(),'No records')]"
        )

        if any(element.is_displayed() for element in no_data):
            raise AssertionError(
                "Achievement record was not added. "
                "After clicking Submit, the Achievement List table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Achievement record was not added. "
        "After clicking Submit, no row appeared in the Achievement List table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No achievement record added. Table body is empty."

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        if all(value in row_text for value in expected_values):
            return True

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Exact achievement row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values, timeout=25):
    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            if len(rows) == 0:
                return True

            deleted_row_found = False

            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in deleted_values):
                    deleted_row_found = True
                    break

            if not deleted_row_found:
                return True

        except StaleElementReferenceException:
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = ""

    raise AssertionError(
        f"Deleted achievement row still found after waiting. "
        f"Deleted values: {deleted_values}. "
        f"Actual table text: {table_text}"
    )


def fill_achievement_form(page, award_name):
    selected_course = page.select_course()
    selected_semester = page.select_semester()
    selected_student = page.select_student()
    page.enter_achievement_date(ACHIEVEMENT_DATE)
    page.enter_award_name(award_name)
    page.upload_file(UPLOAD_FILE_PATH)

    return selected_course, selected_semester, selected_student


def test_achievement_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AchievementPage(driver)

        assert os.path.exists(UPLOAD_FILE_PATH), (
            f"Upload file does not exist: {UPLOAD_FILE_PATH}"
        )

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

        driver.get(ACHIEVEMENT_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "achievement" in driver.current_url.lower()

        add_step(steps, driver, "Open Achievement Awards Page")

        SELECTED_COURSE, SELECTED_SEMESTER, SELECTED_STUDENT = fill_achievement_form(
            page,
            AWARD_NAME
        )

        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Achievement Form With Upload")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Achievement List")

        # ADDED_ROW_VALUES = [
        #     AWARD_NAME,
        #     SELECTED_SEMESTER,
        #     ACHIEVEMENT_DATE,
        #     SELECTED_STUDENT
        # ]
        ADDED_ROW_VALUES = [
            SELECTED_COURSE,
            SELECTED_SEMESTER,
            ACHIEVEMENT_DATE,
            SELECTED_STUDENT
        ]

        verify_exact_table_row_added(
            driver,
            ADDED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Achievement Added")

        page.click_edit_for_exact_row(ADDED_ROW_VALUES)
        wait.until(EC.presence_of_element_located(page.AWARD_NAME))
        add_step(steps, driver, "Click Edit Button For Exact Added Row")

        page.enter_award_name(EDIT_AWARD_NAME)
        page.upload_file(UPLOAD_FILE_PATH)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Achievement Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Achievement List")

        # UPDATED_ROW_VALUES = [
        #     EDIT_AWARD_NAME,
        #     SELECTED_SEMESTER,
        #     ACHIEVEMENT_DATE,
        #     SELECTED_STUDENT
        # ]
        UPDATED_ROW_VALUES = [
            SELECTED_COURSE,
            SELECTED_SEMESTER,
            ACHIEVEMENT_DATE,
            SELECTED_STUDENT
        ]

        verify_exact_table_row_added(
            driver,
            UPDATED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Achievement Updated")

        page.click_delete_for_exact_row(UPDATED_ROW_VALUES)

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(steps, driver, "Click Delete Button For Exact Updated Row")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(2)
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            UPDATED_ROW_VALUES,
            timeout=25
        )
        add_step(steps, driver, "Verify Achievement Deleted")

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
        create_pdf_report("Achievement_Test_Report", steps)