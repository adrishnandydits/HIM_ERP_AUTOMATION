from pages.pre_admission_page import PreAdmissionPage

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
PRE_ADMISSION_URL = "https://devanttest.in/him_test/#/student-information/pre-admission"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

STUDENT_ID = str(RANDOM_NUMBER)
FIRST_NAME = f"TestFirst{RANDOM_NUMBER}"
MIDDLE_NAME = f"TestMiddle{RANDOM_NUMBER}"
LAST_NAME = f"TestLast{RANDOM_NUMBER}"
FULL_NAME = f"{FIRST_NAME} {MIDDLE_NAME} {LAST_NAME}"

EDIT_FIRST_NAME = f"UpdatedFirst{RANDOM_NUMBER}"
EDIT_MIDDLE_NAME = f"UpdatedMiddle{RANDOM_NUMBER}"
EDIT_LAST_NAME = f"UpdatedLast{RANDOM_NUMBER}"
EDIT_FULL_NAME = f"{EDIT_FIRST_NAME} {EDIT_MIDDLE_NAME} {EDIT_LAST_NAME}"

DATE_OF_BIRTH = "13-02-2024"
ADMISSION_DATE = "13-05-2026"
PHONE_NUMBER = f"987655{RANDOM_NUMBER}"
EMERGENCY_CONTACT_NUMBER = f"887655{RANDOM_NUMBER}"
EMAIL_ADDRESS = f"preadmission{RANDOM_NUMBER}@gmail.com"
EDIT_EMAIL_ADDRESS = f"updatedpreadmission{RANDOM_NUMBER}@gmail.com"
CURRENT_ADDRESS = f"Current Address {RANDOM_NUMBER}"
PERMANENT_ADDRESS = f"Permanent Address {RANDOM_NUMBER}"

EDIT_ADMISSION_DATE = "14-05-2026"
EDIT_PHONE_NUMBER = f"797655{RANDOM_NUMBER}"
EDIT_CURRENT_ADDRESS = f"Updated Current Address {RANDOM_NUMBER}"
EDIT_PERMANENT_ADDRESS = f"Updated Permanent Address {RANDOM_NUMBER}"


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

    visible_errors = []

    for error in errors:
        try:
            if error.is_displayed() and error.text.strip():
                visible_errors.append(error.text.strip())
        except StaleElementReferenceException:
            continue

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_table_or_validation(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            errors = driver.find_elements(
                By.XPATH,
                "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
            )

            visible_errors = []

            for error in errors:
                try:
                    if error.is_displayed() and error.text.strip():
                        visible_errors.append(error.text.strip())
                except StaleElementReferenceException:
                    continue

            if visible_errors:
                raise AssertionError(
                    f"Validation error found after save/update: {visible_errors}"
                )

            no_data_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no records')]"
            )

            visible_no_data = []

            for element in no_data_elements:
                try:
                    if element.is_displayed() and element.text.strip():
                        visible_no_data.append(element.text.strip())
                except StaleElementReferenceException:
                    continue

            if visible_no_data:
                raise AssertionError(
                    f"No pre-admission data found. Message shown: {visible_no_data}"
                )

            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                try:
                    if row.is_displayed() and row.text.strip():
                        return True
                except StaleElementReferenceException:
                    continue

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError(
        "Pre-admission table was not loaded. "
        "After clicking Save/Update, no stable row appeared."
    )


def verify_exact_table_row_added(driver, expected_values, timeout=25):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in expected_values):
                    return True

        except StaleElementReferenceException:
            time.sleep(1)

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Exact pre-admission row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table/body text: {table_text}"
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
                try:
                    row_text = " ".join(row.text.lower().split())

                    if all(value in row_text for value in deleted_values):
                        deleted_row_found = True
                        break
                except StaleElementReferenceException:
                    continue

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
        f"Deleted pre-admission row still found after waiting. "
        f"Deleted values: {deleted_values}. "
        f"Actual table text: {table_text}"
    )


def verify_pre_admission_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "pre admission" in page_text, (
        "Pre Admission page heading was not found."
    )

    assert "student pre admission" in page_text, (
        "Student Pre Admission form was not found."
    )

    assert "student id" in page_text, (
        "Student ID field was not found."
    )

    assert "first name" in page_text, (
        "First Name field was not found."
    )

    assert "save student" in page_text, (
        "Save Student button was not found."
    )

    return True


def verify_show_pre_admitted_students_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "show pre-admitted students" in page_text or "pre-admitted students" in page_text, (
        "Show Pre-Admitted Students section was not found."
    )

    assert "search" in page_text, (
        "Search field was not found in Show Pre-Admitted Students list."
    )

    return True


def verify_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "type",
        "email",
        "amount",
        "refund",
        "action"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected Pre Admission table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def fill_pre_admission_form(page):
    page.scroll_page_top()

    page.enter_student_id(STUDENT_ID)
    page.enter_first_name(FIRST_NAME)
    page.enter_middle_name(MIDDLE_NAME)
    page.enter_last_name(LAST_NAME)

    selected_gender = page.select_gender()

    page.enter_date_of_birth(DATE_OF_BIRTH)
    page.enter_admission_date(ADMISSION_DATE)
    page.enter_phone_number(PHONE_NUMBER)
    page.enter_emergency_contact_number(EMERGENCY_CONTACT_NUMBER)

    selected_material_status = page.select_material_status()
    selected_religion = page.select_religion()
    selected_caste = page.select_caste()
    selected_blood_group = page.select_blood_group()
    selected_course = page.select_course()
    selected_semester = page.select_semester()

    page.enter_email_address(EMAIL_ADDRESS)
    page.enter_current_address(CURRENT_ADDRESS)
    page.enter_permanent_address(PERMANENT_ADDRESS)

    return (
        selected_gender,
        selected_material_status,
        selected_religion,
        selected_caste,
        selected_blood_group,
        selected_course,
        selected_semester
    )


def edit_pre_admission_form(page):
    page.scroll_page_top()

    page.enter_first_name(EDIT_FIRST_NAME)
    page.enter_middle_name(EDIT_MIDDLE_NAME)
    page.enter_last_name(EDIT_LAST_NAME)

    page.enter_admission_date(EDIT_ADMISSION_DATE)

    page.enter_phone_number(EDIT_PHONE_NUMBER)
    page.enter_email_address(EDIT_EMAIL_ADDRESS)
    page.enter_current_address(EDIT_CURRENT_ADDRESS)
    page.enter_permanent_address(EDIT_PERMANENT_ADDRESS)


def test_pre_admission_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = PreAdmissionPage(driver)

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

        driver.get(PRE_ADMISSION_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "pre-admission" in driver.current_url.lower()

        add_step(steps, driver, "Open Pre Admission Page")

        verify_pre_admission_page(driver)
        add_step(steps, driver, "Verify Pre Admission Page")

        (
            SELECTED_GENDER,
            SELECTED_MATERIAL_STATUS,
            SELECTED_RELIGION,
            SELECTED_CASTE,
            SELECTED_BLOOD_GROUP,
            SELECTED_COURSE,
            SELECTED_SEMESTER
        ) = fill_pre_admission_form(page)

        add_step(
            steps,
            driver,
            "Fill Pre Admission Form",
            "PASS",
            reason=(
                f"Gender: {SELECTED_GENDER}, "
                f"Material Status: {SELECTED_MATERIAL_STATUS}, "
                f"Religion: {SELECTED_RELIGION}, "
                f"Caste: {SELECTED_CASTE}, "
                f"Blood Group: {SELECTED_BLOOD_GROUP}, "
                f"Course: {SELECTED_COURSE}, "
                f"Semester: {SELECTED_SEMESTER}"
            )
        )

        page.click_save_student()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Save Student Button")

        verify_no_validation_error(driver)

        page.click_show_pre_admitted_students_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Show Pre-Admitted Students Tab")

        verify_show_pre_admitted_students_page(driver)
        add_step(steps, driver, "Verify Show Pre-Admitted Students Page")

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Pre-Admitted Students List")

        page.enter_search_or_filter(EMAIL_ADDRESS)
        add_step(steps, driver, "Search Added Pre-Admitted Student")

        ADDED_ROW_VALUES = [
            FULL_NAME,
            EMAIL_ADDRESS
        ]

        verify_exact_table_row_added(
            driver,
            ADDED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Pre-Admitted Student Added")

        page.click_edit_for_exact_row([EMAIL_ADDRESS])
        wait.until(EC.presence_of_element_located(page.FIRST_NAME))
        add_step(steps, driver, "Click Edit Button For Exact Added Pre-Admitted Student")

        edit_pre_admission_form(page)
        add_step(steps, driver, "Edit Pre Admission Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.click_show_pre_admitted_students_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Show Pre-Admitted Students Tab After Update")

        wait_for_table_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Updated Pre-Admitted Students List")

        page.enter_search_or_filter(EDIT_EMAIL_ADDRESS)
        add_step(steps, driver, "Search Updated Pre-Admitted Student")

        UPDATED_ROW_VALUES = [
            EDIT_FULL_NAME,
            EDIT_EMAIL_ADDRESS
        ]

        verify_exact_table_row_added(
            driver,
            UPDATED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Pre-Admitted Student Updated")

        page.click_delete_for_exact_row([EDIT_EMAIL_ADDRESS])

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
            "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(steps, driver, "Click Delete Button For Exact Updated Pre-Admitted Student")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(2)
        add_step(steps, driver, "Confirm Delete")

        page.enter_search_or_filter(EDIT_EMAIL_ADDRESS)
        add_step(steps, driver, "Search Deleted Pre-Admitted Student")

        verify_exact_table_row_deleted(
            driver,
            [EDIT_EMAIL_ADDRESS],
            timeout=25
        )
        add_step(steps, driver, "Verify Pre-Admitted Student Deleted")

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
        create_pdf_report("Pre_Admission_Test_Report", steps)