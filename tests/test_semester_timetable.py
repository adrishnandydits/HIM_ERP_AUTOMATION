# tests/test_semester_timetable.py

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.semester_timetable_page import SemesterTimetablePage

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanthosting.cloud/him_v2/#/auth/login"

SEMESTER_TIMETABLE_URL = (
    "https://devanthosting.cloud/him_v2/#/academics/semester-timetable"
)

EMAIL = "admin@admin.com"
PASSWORD = "12345678"


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


def verify_semester_timetable_page(driver):

    page_text = " ".join(
        driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower().split()
    )

    assert "semester timetable" in page_text or "semester time table" in page_text

    assert "select course" in page_text

    assert "select semester" in page_text

    assert "search" in page_text

    return True


def verify_timetable_result(driver):

    page_text = " ".join(
        driver.find_element(
            By.TAG_NAME,
            "body"
        ).text.lower().split()
    )

    assert "monday" in page_text
    assert "tuesday" in page_text
    assert "wednesday" in page_text
    assert "thursday" in page_text
    assert "friday" in page_text

    assert "room:" in page_text

    return True


def test_semester_timetable_search_flow(driver):

    steps = []

    wait = WebDriverWait(driver, 20)

    try:

        page = SemesterTimetablePage(driver)

        driver.get(LOGIN_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        add_step(
            steps,
            driver,
            "Open Login Page"
        )

        page.enter_text(
            page.EMAIL,
            EMAIL
        )

        add_step(
            steps,
            driver,
            "Enter Email"
        )

        page.enter_text(
            page.PASSWORD,
            PASSWORD
        )

        add_step(
            steps,
            driver,
            "Enter Password"
        )

        page.click(
            page.LOGIN_BUTTON
        )

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        add_step(
            steps,
            driver,
            "Click Login Button"
        )

        driver.get(SEMESTER_TIMETABLE_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        add_step(
            steps,
            driver,
            "Open Semester Timetable Page"
        )

        verify_semester_timetable_page(driver)

        add_step(
            steps,
            driver,
            "Verify Semester Timetable Page"
        )

        selected_course = page.select_course()

        add_step(
            steps,
            driver,
            "Select Course",
            "PASS",
            reason=f"Selected Course: {selected_course}"
        )

        selected_semester = page.select_semester()

        add_step(
            steps,
            driver,
            "Select Semester",
            "PASS",
            reason=f"Selected Semester: {selected_semester}"
        )

        page.click_search()

        add_step(
            steps,
            driver,
            "Click Search Button"
        )

        page.wait_for_timetable_result(timeout=30)

        add_step(
            steps,
            driver,
            "Load Semester Timetable Result"
        )

        verify_timetable_result(driver)

        add_step(
            steps,
            driver,
            "Verify Semester Timetable Data"
        )

    except Exception as e:

        error_reason = str(e).strip()

        if not error_reason:
            error_reason = "No detailed error message returned."

        error_reason = (
            f"{type(e).__name__}: {error_reason}"
        )

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

        create_pdf_report(
            "Semester_Timetable_Test_Report",
            steps
        )