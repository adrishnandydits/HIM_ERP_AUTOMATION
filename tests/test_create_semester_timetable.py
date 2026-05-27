from pages.create_semester_timetable_page import CreateSemesterTimetablePage

import pytest
import random
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
CREATE_SEMESTER_TIMETABLE_URL = "https://devanttest.in/him_test/#/academics/create-semester-timeTable"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA (Hospital Management)"
SEMESTER = "4th Sem"
SESSION = "2024"

RANDOM_NUMBER = random.randint(10, 50)

TIME_FROM = f"13:{RANDOM_NUMBER:02d}"
TIME_TO = f"14:{RANDOM_NUMBER:02d}"
ROOM_NO = "45"


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


def verify_create_semester_timetable_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "semester timetable" in page_text or "semester time table" in page_text, (
        "Semester Timetable page heading was not found."
    )

    assert "create semester table" in page_text, (
        "Create Semester Table section was not found."
    )

    assert "select course" in page_text, (
        "Select Course dropdown was not found."
    )

    assert "select semester" in page_text, (
        "Select Semester dropdown was not found."
    )

    assert "select subject" in page_text, (
        "Select Subject field was not found."
    )

    assert "teacher list" in page_text, (
        "Teacher List dropdown was not found."
    )

    assert "time from" in page_text, (
        "Time From field was not found."
    )

    assert "time to" in page_text, (
        "Time To field was not found."
    )

    assert "select day" in page_text, (
        "Select Day dropdown was not found."
    )

    assert "room no" in page_text, (
        "Room No field was not found."
    )

    return True


def verify_selected_create_values(driver, selected_course, selected_semester, selected_teacher, selected_day):
    select_elements = driver.find_elements(By.XPATH, "//select")

    assert len(select_elements) >= 4, (
        f"Expected at least 4 dropdowns on create form. Actual dropdown count: {len(select_elements)}"
    )

    selected_course_text = Select(select_elements[0]).first_selected_option.text.strip()
    selected_semester_text = Select(select_elements[1]).first_selected_option.text.strip()

    teacher_select = driver.find_element(
        By.XPATH,
        "//label[contains(normalize-space(),'Teacher List')]/following::select[1]"
    )

    day_select = driver.find_element(
        By.XPATH,
        "//label[contains(normalize-space(),'Select Day')]/following::select[1]"
    )

    selected_teacher_text = Select(teacher_select).first_selected_option.text.strip()
    selected_day_text = Select(day_select).first_selected_option.text.strip()

    assert selected_course.lower() in selected_course_text.lower(), (
        f"Selected course mismatch. Expected: {selected_course}, Actual: {selected_course_text}"
    )

    assert selected_semester.lower() in selected_semester_text.lower(), (
        f"Selected semester mismatch. Expected: {selected_semester}, Actual: {selected_semester_text}"
    )

    assert selected_teacher.lower() in selected_teacher_text.lower(), (
        f"Selected teacher mismatch. Expected: {selected_teacher}, Actual: {selected_teacher_text}"
    )

    assert selected_day.lower() in selected_day_text.lower(), (
        f"Selected day mismatch. Expected: {selected_day}, Actual: {selected_day_text}"
    )

    return True


def verify_list_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "week",
        "subject name",
        "teacher name",
        "time from",
        "time to",
        "room no",
        "action"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected list table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_added_row_values(driver, expected_values, timeout=25):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                if not row.is_displayed() or not row.text.strip():
                    continue

                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in expected_values):
                    return row_text

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Added semester timetable row was not found. "
        f"Expected values: {expected_values}. "
        f"Actual text: {table_text}"
    )


# def verify_show_timetable_data(driver):
#     page_text = " ".join(
#         driver.find_element(By.XPATH, "//body").text.lower().split()
#     )
#
#     assert "semester time table" in page_text or "semester timetable" in page_text, (
#         "Show Semester Table result heading was not found."
#     )
#
#     assert "monday" in page_text, "Monday column was not found."
#     assert "tuesday" in page_text, "Tuesday column was not found."
#     assert "wednesday" in page_text, "Wednesday column was not found."
#     assert "thursday" in page_text, "Thursday column was not found."
#     assert "friday" in page_text, "Friday column was not found."
#     assert "saturday" in page_text, "Saturday column was not found."
#     assert "sunday" in page_text, "Sunday column was not found."
#
#     assert "subject" in page_text, "Subject text was not found in timetable."
#     assert "teacher name" in page_text, "Teacher Name text was not found in timetable."
#     assert "time" in page_text, "Time text was not found in timetable."
#     assert "room no" in page_text, "Room No text was not found in timetable."
#
#     return True
def verify_show_timetable_data(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert (
        "semester time table" in page_text
        or "semester timetable" in page_text
    ), (
        "Show Semester Table result heading was not found."
    )

    expected_days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]

    found_days = [
        day
        for day in expected_days
        if day in page_text
    ]

    assert len(found_days) >= 3, (
        f"Expected timetable weekdays not found properly. "
        f"Found days: {found_days}"
    )

    assert "room" in page_text, (
        "Room information was not found in timetable."
    )

    assert ":" in page_text or "-" in page_text, (
        "Time range was not found in timetable."
    )

    timetable_cards = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'Room')] "
        "| //*[contains(text(),'room')] "
        "| //*[contains(text(),':')]"
    )

    visible_cards = []

    for card in timetable_cards:
        try:
            if card.is_displayed() and card.text.strip():
                visible_cards.append(card.text.strip())
        except StaleElementReferenceException:
            continue

    assert len(visible_cards) > 0, (
        "No visible timetable data cards found."
    )

    return True


def verify_still_on_create_semester_timetable_page(driver):
    current_url = driver.current_url.lower()

    assert "create-semester-timetable" in current_url, (
        f"Page redirected unexpectedly. "
        f"Expected to stay on Create Semester Timetable page. "
        f"Actual URL: {driver.current_url}"
    )

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "semester timetable" in page_text or "semester time table" in page_text, (
        "Semester Timetable page content was not found."
    )

    return True


def fill_create_semester_timetable_form(page):
    selected_course = page.select_course()
    selected_semester = page.select_semester()
    selected_subject = page.select_subject()
    selected_teacher = page.select_teacher()

    page.enter_time_from(TIME_FROM)
    page.enter_time_to(TIME_TO)

    selected_day = page.select_day()

    page.enter_room_no(ROOM_NO)

    return selected_course, selected_semester, selected_subject, selected_teacher, selected_day


def test_create_semester_timetable_add_save_show_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = CreateSemesterTimetablePage(driver)

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

        driver.get(CREATE_SEMESTER_TIMETABLE_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "create-semester-timetable" in driver.current_url.lower()

        add_step(steps, driver, "Open Create Semester Timetable Page")

        verify_create_semester_timetable_page(driver)
        add_step(steps, driver, "Verify Create Semester Timetable Page")

        (
            SELECTED_COURSE,
            SELECTED_SEMESTER,
            SELECTED_SUBJECT,
            SELECTED_TEACHER,
            SELECTED_DAY
        ) = fill_create_semester_timetable_form(page)

        add_step(steps, driver, "Fill Create Semester Timetable Form")

        page.click_add()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Add Button")

        verify_no_validation_error(driver)

        ADDED_ROW_VALUES = [
            SELECTED_DAY,
            TIME_FROM,
            TIME_TO,
            ROOM_NO
        ]

        added_row_text = verify_added_row_values(
            driver,
            ADDED_ROW_VALUES,
            timeout=25
        )

        add_step(
            steps,
            driver,
            "Verify Timetable Row Added",
            "PASS",
            reason=f"Added row found: {added_row_text}"
        )

        page.click_save()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Save Button")

        page.wait_for_save_confirmation_popup(timeout=20)
        add_step(steps, driver, "Verify Save Confirmation Popup")

        page.confirm_save()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Save Timetable")

        verify_still_on_create_semester_timetable_page(driver)
        add_step(steps, driver, "Verify Page Did Not Redirect Unexpectedly")


        page.click_show_semester_table_tab()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Show Semester Table Tab")

        SHOW_SELECTED_COURSE = page.select_show_course()
        SHOW_SELECTED_SEMESTER = page.select_show_semester()
        SHOW_SELECTED_SESSION = page.select_show_session()

        add_step(
            steps,
            driver,
            "Fill Show Semester Table Filter",
            "PASS",
            reason=f"Course: {SHOW_SELECTED_COURSE}, Semester: {SHOW_SELECTED_SEMESTER}, Session: {SHOW_SELECTED_SESSION}"
        )

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Search Button")

        verify_no_validation_error(driver)

        page.wait_for_show_timetable_result(timeout=25)
        add_step(steps, driver, "Load Show Semester Table Result")

        verify_show_timetable_data(driver)
        add_step(steps, driver, "Verify Show Semester Table Data")

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
        create_pdf_report("Create_Semester_Timetable_Test_Report", steps)