from pages.add_staff_page import AddStaffPage

import os
import pytest
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
ADD_STAFF_URL = "https://devanttest.in/him_test/#/human-resource/add-staff"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

STAFF_ID = f"STF{RANDOM_NUMBER}"
FIRST_NAME = f"test{RANDOM_NUMBER}"
MIDDLE_NAME = "forg"
LAST_NAME = "pass"

EDIT_FIRST_NAME = f"test edited {RANDOM_NUMBER}"

GENDER = "Male"
DATE_OF_BIRTH = "2025-11-24"
DATE_OF_JOINING = "2026-05-07"
PHONE_NUMBER = "9876543210"
EMERGENCY_CONTACT_NUMBER = "9876543211"
WORK_EXPERIENCE = "2"
QUALIFICATION = "M.Pharm"
EMAIL_ADDRESS = f"teststaff{RANDOM_NUMBER}@gmail.com"
CURRENT_ADDRESS = "test current address"
PERMANENT_ADDRESS = "test permanent address"
PAN_NUMBER = "ABCDE1234F"

EPF_NUMBER = "EPF1001"
GROSS_SALARY = "25000"
LOCATION = "Kolkata"

BANK_ACCOUNT_NUMBER = "123456789012"
BANK_NAME = "SBI"
IFSC_CODE = "SBIN0001234"
BANK_BRANCH_NAME = "Kolkata Branch"

UPLOAD_FILE_PATH = r"C:\Users\Devant\Downloads\Group 3621.png"


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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")

    assert len(file_inputs) > 0, "No file input found on the page"

    for file_input in file_inputs:
        uploaded_file_value = file_input.get_attribute("value")
        assert uploaded_file_value != "", "File was not uploaded into input"

    return True


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No staff record added. Table body is empty."

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
        f"Exact staff row not found. "
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
            f"Deleted staff row still found. "
            f"Deleted values: {deleted_values}. "
            f"Row text: {row.text}"
        )

    return True


def fill_staff_basic_form(page):
    page.enter_staff_id(STAFF_ID)
    page.enter_first_name(FIRST_NAME)
    page.enter_middle_name(MIDDLE_NAME)
    page.enter_last_name(LAST_NAME)

    page.select_gender()
    page.enter_date_of_birth(DATE_OF_BIRTH)
    page.enter_date_of_joining(DATE_OF_JOINING)
    page.enter_phone_number(PHONE_NUMBER)

    page.enter_emergency_contact_number(EMERGENCY_CONTACT_NUMBER)
    page.select_material_status()
    page.enter_work_experience(WORK_EXPERIENCE)
    page.enter_qualification(QUALIFICATION)

    page.select_blood_group()
    page.select_religion()
    page.select_user_type()
    page.enter_email_address(EMAIL_ADDRESS)

    page.select_caste()
    page.select_department()
    page.select_franchise()
    page.select_designation()

    page.enter_current_address(CURRENT_ADDRESS)
    page.enter_permanent_address(PERMANENT_ADDRESS)
    page.enter_pan_number(PAN_NUMBER)


def fill_payroll_form(page):
    page.enter_epf_number(EPF_NUMBER)
    page.enter_gross_salary(GROSS_SALARY)
    page.enter_location(LOCATION)
    page.select_contract_type()


def fill_bank_account_form(page):
    page.enter_bank_account_number(BANK_ACCOUNT_NUMBER)
    page.enter_bank_name(BANK_NAME)
    page.enter_ifsc_code(IFSC_CODE)
    page.enter_bank_branch_name(BANK_BRANCH_NAME)


def test_add_staff_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = AddStaffPage(driver)

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

        driver.get(ADD_STAFF_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        assert "add-staff" in driver.current_url.lower()
        add_step(steps, driver, "Open Add Staff Page")

        fill_staff_basic_form(page)
        add_step(steps, driver, "Fill Staff Form")

        page.click_next()
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='file']")))
        add_step(steps, driver, "Click Next To Upload Documents")

        page.upload_staff_documents(UPLOAD_FILE_PATH)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Upload Staff Documents")

        page.click_next()
        wait.until(EC.presence_of_element_located(page.EPF_NUMBER))
        add_step(steps, driver, "Click Next To Payroll")

        fill_payroll_form(page)
        add_step(steps, driver, "Fill Payroll Form")

        page.click_next()
        wait.until(EC.presence_of_element_located(page.BANK_ACCOUNT_NUMBER))
        add_step(steps, driver, "Click Next To Bank Account Details")

        fill_bank_account_form(page)
        add_step(steps, driver, "Fill Bank Account Details")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_staff()
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Open Show Staff Page")

        verify_exact_table_row_added(
            driver,
            [FIRST_NAME]
        )
        add_step(steps, driver, "Verify Staff Added")

        page.click_edit()
        page.click_fill_form()
        wait.until(EC.presence_of_element_located(page.FIRST_NAME))
        add_step(steps, driver, "Click Edit Button")

        page.enter_first_name(EDIT_FIRST_NAME)
        add_step(steps, driver, "Edit First Name")

        page.click_bank_account_details()

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.click_show_staff()
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Open Show Staff Page After Update")

        verify_exact_table_row_added(
            driver,
            [EDIT_FIRST_NAME]
        )
        add_step(steps, driver, "Verify Staff Updated")

        page.click_delete()
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'delete')]"
                )
            )
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            [EDIT_FIRST_NAME]
        )
        add_step(steps, driver, "Verify Staff Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Add_Staff_Test_Report", steps)