from pages.education_qualification_page import EducationQualificationPage

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
EDUCATION_QUALIFICATION_URL = "https://devanttest.in/him_test/#/student-information/education-qualification"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

CLASS_10_BOARD = f"Class 10 Board {RANDOM_NUMBER}"
CLASS_10_MARKS = "430"
CLASS_10_PERCENTAGE = "76"
CLASS_10_DIVISION = "First"
CLASS_10_MAIN_SUBJECT = "General"
CLASS_10_YEAR = "2022"

CLASS_12_BOARD = f"Class 12 Board {RANDOM_NUMBER}"
CLASS_12_MARKS = "340"
CLASS_12_PERCENTAGE = "45"
CLASS_12_DIVISION = "Second"
CLASS_12_MAIN_SUBJECT = "Science"
CLASS_12_YEAR = "2024"

GRADUATION_BOARD = f"Graduation Board {RANDOM_NUMBER}"
GRADUATION_MARKS = "670"
GRADUATION_PERCENTAGE = "67"
GRADUATION_DIVISION = "First"
GRADUATION_MAIN_SUBJECT = "Pharmacy"
GRADUATION_YEAR = "2026"


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


def verify_education_qualification_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "education qualification" in page_text, (
        "Education Qualification page heading was not found."
    )

    assert "add education qualification" in page_text, (
        "Add Education Qualification section was not found."
    )

    assert "select course" in page_text, (
        "Select Course dropdown was not found."
    )

    assert "select semester" in page_text, (
        "Select Semester dropdown was not found."
    )

    assert "select student" in page_text, (
        "Select Student dropdown was not found."
    )

    assert "class 10th" in page_text or "m.p" in page_text, (
        "Class 10th section was not found."
    )

    assert "10+2" in page_text or "h.s" in page_text, (
        "10+2 section was not found."
    )

    assert "graduation" in page_text, (
        "Graduation section was not found."
    )

    return True


def verify_show_education_qualification_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "show education qualification" in page_text or "education qualification" in page_text, (
        "Show Education Qualification section was not found."
    )

    assert "select course" in page_text, (
        "Select Course field was not found in Show tab."
    )

    assert "select semester" in page_text, (
        "Select Semester field was not found in Show tab."
    )

    assert "select student" in page_text, (
        "Select Student field was not found in Show tab."
    )

    assert "search" in page_text, (
        "Search button was not found in Show tab."
    )

    return True


def wait_for_result_or_validation(driver, timeout=25):
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
                    f"Validation error found: {visible_errors}"
                )

            no_data_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'not found') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'data not found')]"
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
                    f"No education qualification data found. Message shown: {visible_no_data}"
                )

            body_text = " ".join(
                driver.find_element(By.XPATH, "//body").text.lower().split()
            )

            if (
                "class 10" in body_text
                or "10+2" in body_text
                or "graduation" in body_text
                or CLASS_10_BOARD.lower() in body_text
                or CLASS_12_BOARD.lower() in body_text
                or GRADUATION_BOARD.lower() in body_text
            ):
                return True

            tables = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in tables:
                try:
                    if row.is_displayed() and row.text.strip():
                        return True
                except StaleElementReferenceException:
                    continue

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError(
        "Education Qualification result was not loaded."
    )


def verify_added_qualification_data(driver):
    body_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    expected_values = [
        CLASS_10_BOARD.lower(),
        CLASS_10_MARKS.lower(),
        CLASS_10_PERCENTAGE.lower(),
        CLASS_10_YEAR.lower(),
        CLASS_12_BOARD.lower(),
        CLASS_12_MARKS.lower(),
        CLASS_12_PERCENTAGE.lower(),
        CLASS_12_YEAR.lower(),
        GRADUATION_BOARD.lower(),
        GRADUATION_PERCENTAGE.lower(),
        GRADUATION_YEAR.lower()
    ]

    missing_values = []

    for value in expected_values:
        if value not in body_text:
            missing_values.append(value)

    assert len(missing_values) == 0, (
        f"Education qualification data was not verified. "
        f"Missing values: {missing_values}. "
        f"Actual page text: {body_text[:1500]}"
    )

    return True


def fill_education_qualification_form(page):
    page.scroll_page_top()

    selected_course = page.select_course()
    selected_semester = page.select_semester()
    selected_student = page.select_student()

    page.enter_class_10_details(
        CLASS_10_BOARD,
        CLASS_10_MARKS,
        CLASS_10_PERCENTAGE,
        CLASS_10_DIVISION,
        CLASS_10_MAIN_SUBJECT,
        CLASS_10_YEAR
    )

    page.enter_class_12_details(
        CLASS_12_BOARD,
        CLASS_12_MARKS,
        CLASS_12_PERCENTAGE,
        CLASS_12_DIVISION,
        CLASS_12_MAIN_SUBJECT,
        CLASS_12_YEAR
    )

    page.scroll_page_bottom()

    page.enter_graduation_details(
        GRADUATION_BOARD,
        GRADUATION_MARKS,
        GRADUATION_PERCENTAGE,
        GRADUATION_DIVISION,
        GRADUATION_MAIN_SUBJECT,
        GRADUATION_YEAR
    )

    return selected_course, selected_semester, selected_student


def test_education_qualification_add_show_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = EducationQualificationPage(driver)

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

        driver.get(EDUCATION_QUALIFICATION_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "education-qualification" in driver.current_url.lower()

        add_step(steps, driver, "Open Education Qualification Page")

        verify_education_qualification_page(driver)
        add_step(steps, driver, "Verify Education Qualification Page")

        (
            SELECTED_COURSE,
            SELECTED_SEMESTER,
            SELECTED_STUDENT
        ) = fill_education_qualification_form(page)

        add_step(
            steps,
            driver,
            "Fill Education Qualification Form",
            "PASS",
            reason=(
                f"Course: {SELECTED_COURSE}, "
                f"Semester: {SELECTED_SEMESTER}, "
                f"Student: {SELECTED_STUDENT}"
            )
        )

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_education_qualification_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Show Education Qualification Tab")

        verify_show_education_qualification_page(driver)
        add_step(steps, driver, "Verify Show Education Qualification Page")

        SHOW_SELECTED_COURSE = page.select_course()
        SHOW_SELECTED_SEMESTER = page.select_semester()
        SHOW_SELECTED_STUDENT = page.select_student()

        add_step(
            steps,
            driver,
            "Fill Show Education Qualification Filter",
            "PASS",
            reason=(
                f"Course: {SHOW_SELECTED_COURSE}, "
                f"Semester: {SHOW_SELECTED_SEMESTER}, "
                f"Student: {SHOW_SELECTED_STUDENT}"
            )
        )

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_result_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Education Qualification Result")

        verify_added_qualification_data(driver)
        add_step(steps, driver, "Verify Education Qualification Data")

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
        create_pdf_report("Education_Qualification_Test_Report", steps)