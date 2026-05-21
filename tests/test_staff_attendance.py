from pages.staff_attendance_page import StaffAttendancePage

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
STAFF_ATTENDANCE_URL = "https://devanttest.in/him_test/#/human-resource/staff-attendance"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

USER_TYPE = "Teacher"
SELECT_DATE = "2026-05-07"

ATTENDANCE_OPTIONS = ["Present", "Absent", "Late", "Half day"]


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


def verify_staff_list_loaded(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, "No staff attendance list found. Table body is empty."

    return True


def verify_attendance_table_loaded(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, "No staff attendance list found. Table body is empty."

    table_text = driver.find_element(By.XPATH, "//table//tbody").text
    normalized_text = " ".join(table_text.lower().split())

    expected_values = [
        value.lower().strip()
        for value in ATTENDANCE_OPTIONS
    ]

    for value in expected_values:
        assert value in normalized_text, (
            f"Attendance option not found: {value}. "
            f"Actual table text: {table_text}"
        )

    return True


def test_staff_attendance_search_and_submit_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = StaffAttendancePage(driver)

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

        driver.get(STAFF_ATTENDANCE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "staff-attendance" in driver.current_url.lower()

        add_step(steps, driver, "Open Staff Attendance Page")

        page.select_user_type()
        add_step(steps, driver, "Select User Type")

        page.enter_select_date(SELECT_DATE)
        add_step(steps, driver, "Enter Select Date")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Click Search Button")

        verify_staff_list_loaded(driver)
        verify_attendance_table_loaded(driver)
        add_step(steps, driver, "Verify Staff List Loaded")

        page.mark_first_staff_present()
        add_step(steps, driver, "Mark First Staff Present")

        page.mark_staff_absent_by_row_number(2)
        add_step(steps, driver, "Mark Second Staff Absent")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        verify_attendance_table_loaded(driver)
        add_step(steps, driver, "Verify Staff Attendance Submitted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Staff_Attendance_Test_Report", steps)