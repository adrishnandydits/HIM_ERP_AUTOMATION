from pages.internship_page import InternshipDetailsPage

import os
import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
INTERNSHIP_DETAILS_URL = "https://devanttest.in/him_test/#/internship/internship"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA (Hospital Management)"
SEMESTER = "3rd Sem"
PROVIDER = "Amazon"
STUDENT = "Biswajit Ghorai"

FROM_DATE = "2026-05-09"
TO_DATE = "2026-05-10"

EDIT_TO_DATE = "2026-05-11"

UPLOAD_FILE_PATH = r"C:\Users\Devant\Downloads\CLASS XII.pdf"


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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")

    assert len(file_inputs) > 0, "No file input found on the page"

    uploaded_file_value = file_inputs[0].get_attribute("value")

    assert uploaded_file_value != "", "Internship file was not uploaded"

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

        time.sleep(1)

    raise AssertionError(
        "Internship details record was not added. "
        "After clicking Submit, no row appeared in the Internship Details table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No internship details record added. Table body is empty."

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
        f"Exact internship details row not found. "
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
            f"Deleted internship details row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def fill_internship_details_form(page, to_date):
    page.select_course()
    page.select_semester()
    page.select_provider()
    page.select_student()
    page.enter_from_date(FROM_DATE)
    page.enter_to_date(to_date)


def test_internship_details_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = InternshipDetailsPage(driver)

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

        driver.get(INTERNSHIP_DETAILS_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "internship" in driver.current_url.lower()

        add_step(steps, driver, "Open Internship Details Page")

        fill_internship_details_form(page, TO_DATE)
        add_step(steps, driver, "Fill Internship Details Form With Upload")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Internship Details List")

        verify_exact_table_row_added(
            driver,
            [PROVIDER, STUDENT]
        )
        add_step(steps, driver, "Verify Internship Details Added")

        page.click_edit()
        wait.until(EC.presence_of_element_located(page.TO_DATE))
        add_step(steps, driver, "Click Edit Button")

        fill_internship_details_form(page, TO_DATE)
        add_step(steps, driver, "Fill Internship Details Form With Upload")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Internship Details List")

        add_step(steps, driver, "Verify Internship Details Updated")

        page.click_delete()

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [PROVIDER, STUDENT, FROM_DATE, EDIT_TO_DATE]
        )
        add_step(steps, driver, "Verify Internship Details Deleted")

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
        create_pdf_report("Internship_Details_Test_Report", steps)