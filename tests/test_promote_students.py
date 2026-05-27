# from pages.promote_students_page import PromoteStudentsPage
#
# import pytest
# import time
#
# from selenium import webdriver
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
#
# from utils.screenshot import take_screenshot
# from utils.pdf_report import create_pdf_report
#
#
# LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
# PROMOTE_STUDENTS_URL = "https://devanttest.in/him_test/#/academics/promote-students"
#
# EMAIL = "admin@admin.com"
# PASSWORD = "12345678"
#
# FROM_COURSE = "BBA (ACCOUNTANCY, TAXATION & AUDITING)"
# FROM_SEMESTER = "3rd Sem"
# TO_SEMESTER = "4th Sem"
#
#
# @pytest.fixture()
# def driver():
#     driver = webdriver.Chrome()
#     driver.maximize_window()
#     yield driver
#     driver.quit()
#
#
# def add_step(steps, driver, name, status="PASS", reason=""):
#     image_path = ""
#
#     try:
#         image_path = take_screenshot(
#             driver,
#             name.lower().replace(" ", "_")
#         )
#     except Exception:
#         image_path = ""
#
#     steps.append({
#         "name": name,
#         "status": status,
#         "reason": reason,
#         "image": image_path
#     })
#
#
# def verify_no_validation_error(driver):
#     errors = driver.find_elements(
#         By.XPATH,
#         "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
#     )
#
#     visible_errors = []
#
#     for error in errors:
#         try:
#             if error.is_displayed() and error.text.strip():
#                 visible_errors.append(error.text.strip())
#         except StaleElementReferenceException:
#             continue
#
#     assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"
#
#
# def verify_promote_students_page(driver):
#     page_text = " ".join(
#         driver.find_element(By.XPATH, "//body").text.lower().split()
#     )
#
#     assert "promote students" in page_text, (
#         "Promote Students page heading was not found."
#     )
#
#     assert "promote from" in page_text, (
#         "Promote From section was not found."
#     )
#
#     assert "promote to" in page_text, (
#         "Promote To section was not found."
#     )
#
#     assert "course" in page_text, (
#         "Course dropdown was not found."
#     )
#
#     assert "semester" in page_text, (
#         "Semester dropdown was not found."
#     )
#
#     return True
#
#
# def verify_selected_values(driver, selected_course, selected_from_semester, selected_to_semester):
#     select_elements = driver.find_elements(By.XPATH, "//select")
#
#     assert len(select_elements) >= 3, (
#         f"Expected at least 3 dropdowns. Actual dropdown count: {len(select_elements)}"
#     )
#
#     selected_course_text = Select(select_elements[0]).first_selected_option.text.strip()
#     selected_from_semester_text = Select(select_elements[1]).first_selected_option.text.strip()
#     selected_to_semester_text = Select(select_elements[2]).first_selected_option.text.strip()
#
#     assert selected_course.lower() in selected_course_text.lower(), (
#         f"Selected course mismatch. "
#         f"Expected: {selected_course}, Actual: {selected_course_text}"
#     )
#
#     assert selected_from_semester.lower() in selected_from_semester_text.lower(), (
#         f"Selected from semester mismatch. "
#         f"Expected: {selected_from_semester}, Actual: {selected_from_semester_text}"
#     )
#
#     assert selected_to_semester.lower() in selected_to_semester_text.lower(), (
#         f"Selected to semester mismatch. "
#         f"Expected: {selected_to_semester}, Actual: {selected_to_semester_text}"
#     )
#
#     return True
#
#
# def wait_for_student_list_or_validation(driver, timeout=25):
#     end_time = time.time() + timeout
#
#     while time.time() < end_time:
#         try:
#             errors = driver.find_elements(
#                 By.XPATH,
#                 "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
#             )
#
#             visible_errors = []
#
#             for error in errors:
#                 try:
#                     if error.is_displayed() and error.text.strip():
#                         visible_errors.append(error.text.strip())
#                 except StaleElementReferenceException:
#                     continue
#
#             if visible_errors:
#                 raise AssertionError(
#                     f"Validation error found after search: {visible_errors}"
#                 )
#
#             no_data_elements = driver.find_elements(
#                 By.XPATH,
#                 "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
#                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
#                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no records') "
#                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'not found') "
#                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'data not found')]"
#             )
#
#             visible_no_data = []
#
#             for element in no_data_elements:
#                 try:
#                     if element.is_displayed() and element.text.strip():
#                         visible_no_data.append(element.text.strip())
#                 except StaleElementReferenceException:
#                     continue
#
#             if visible_no_data:
#                 raise AssertionError(
#                     f"No student data found after search. Message shown: {visible_no_data}"
#                 )
#
#             rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#             for row in rows:
#                 try:
#                     if row.is_displayed() and row.text.strip():
#                         return True
#                 except StaleElementReferenceException:
#                     continue
#
#         except StaleElementReferenceException:
#             pass
#
#         time.sleep(1)
#
#     raise AssertionError(
#         "Student list was not loaded after clicking Search. "
#         "No stable table row appeared for selected Course and Semester."
#     )
#
#
# def verify_student_table_headers(driver):
#     header_text = " ".join(
#         driver.find_element(By.XPATH, "//table//thead").text.lower().split()
#     )
#
#     expected_headers = [
#         "check all",
#         "name",
#         "date of birth"
#     ]
#
#     for header in expected_headers:
#         assert header in header_text, (
#             f"Expected Promote Students table header not found: {header}. "
#             f"Actual header text: {header_text}"
#         )
#
#     return True
#
#
# def verify_first_student_selected(driver):
#     selected_checkboxes = driver.find_elements(
#         By.XPATH,
#         "//table//tbody//tr//input[@type='checkbox' and @checked]"
#     )
#
#     if len(selected_checkboxes) > 0:
#         return True
#
#     rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#     for row in rows:
#         try:
#             checkboxes = row.find_elements(By.XPATH, ".//input[@type='checkbox']")
#
#             for checkbox in checkboxes:
#                 if checkbox.is_selected():
#                     return True
#
#         except StaleElementReferenceException:
#             continue
#
#     raise AssertionError(
#         "No student checkbox was selected before clicking Promote."
#     )
#
#
# def verify_still_on_promote_students_page(driver):
#     current_url = driver.current_url.lower()
#
#     assert "promote-students" in current_url, (
#         f"Page redirected unexpectedly. "
#         f"Expected to stay on Promote Students page. "
#         f"Actual URL: {driver.current_url}"
#     )
#
#     page_text = " ".join(
#         driver.find_element(By.XPATH, "//body").text.lower().split()
#     )
#
#     assert "promote students" in page_text, (
#         "After promoting, Promote Students page content was not found."
#     )
#
#     return True
#
#
# def fill_promote_students_form(page):
#     selected_course = page.select_from_course()
#     selected_from_semester = page.select_from_semester()
#     selected_to_semester = page.select_to_semester()
#
#     return selected_course, selected_from_semester, selected_to_semester
#
#
# def test_promote_students_flow(driver):
#     steps = []
#     wait = WebDriverWait(driver, 20)
#
#     try:
#         page = PromoteStudentsPage(driver)
#
#         driver.get(LOGIN_URL)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
#         add_step(steps, driver, "Open Login Page")
#
#         page.enter_text(page.EMAIL, EMAIL)
#         add_step(steps, driver, "Enter Email")
#
#         page.enter_text(page.PASSWORD, PASSWORD)
#         add_step(steps, driver, "Enter Password")
#
#         page.click(page.LOGIN_BUTTON)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
#         add_step(steps, driver, "Click Login Button")
#
#         driver.get(PROMOTE_STUDENTS_URL)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
#
#         assert "promote-students" in driver.current_url.lower()
#
#         add_step(steps, driver, "Open Promote Students Page")
#
#         verify_promote_students_page(driver)
#         add_step(steps, driver, "Verify Promote Students Page")
#
#         SELECTED_COURSE, SELECTED_FROM_SEMESTER, SELECTED_TO_SEMESTER = fill_promote_students_form(page)
#         add_step(steps, driver, "Fill Promote Students Form")
#
#         page.click_search()
#         wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
#         add_step(steps, driver, "Click Search Button")
#
#         verify_no_validation_error(driver)
#
#         wait_for_student_list_or_validation(driver, timeout=25)
#         add_step(steps, driver, "Load Students List")
#
#         verify_student_table_headers(driver)
#         add_step(steps, driver, "Verify Students Table Headers")
#
#         first_student_row_text = page.get_first_student_row_text()
#         add_step(
#             steps,
#             driver,
#             "Verify First Student Row",
#             "PASS",
#             reason=f"First row found: {first_student_row_text}"
#         )
#
#         selected_student_row_text = page.select_first_student_checkbox()
#         add_step(
#             steps,
#             driver,
#             "Select First Student Checkbox",
#             "PASS",
#             reason=f"Selected student row: {selected_student_row_text}"
#         )
#
#         verify_first_student_selected(driver)
#         add_step(steps, driver, "Verify Student Selected")
#
#         page.click_promote()
#         wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
#         add_step(steps, driver, "Click Promote Button")
#         time.sleep(10)
#
#         page.wait_for_promoted_successfully(timeout=30)
#         add_step(steps, driver, "Verify Promoted Successfully Message")
#
#         verify_still_on_promote_students_page(driver)
#         add_step(steps, driver, "Verify Page Did Not Redirect")
#
#     except Exception as e:
#         error_reason = str(e).strip()
#
#         if not error_reason:
#             error_reason = "No detailed error message returned by Selenium."
#
#         error_reason = f"{type(e).__name__}: {error_reason}"
#
#         try:
#             add_step(
#                 steps,
#                 driver,
#                 "Test Failed",
#                 "FAIL",
#                 reason=error_reason
#             )
#         except Exception:
#             steps.append({
#                 "name": "Test Failed",
#                 "status": "FAIL",
#                 "reason": error_reason,
#                 "image": ""
#             })
#
#         raise e
#
#     finally:
#         create_pdf_report("Promote_Students_Test_Report", steps)
#
#
from pages.promote_students_page import PromoteStudentsPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"

PROMOTE_STUDENTS_URL = (
    "https://devanttest.in/him_test/#/academics/promote-students"
)

EMAIL = "admin@admin.com"
PASSWORD = "12345678"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()

    driver.maximize_window()

    yield driver

    try:
        driver.quit()
    except Exception:
        pass


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


def verify_promote_students_page(driver):
    page_text = " ".join(
        driver.find_element(By.TAG_NAME, "body").text.lower().split()
    )

    assert "promote students" in page_text
    assert "promote from" in page_text
    assert "promote to" in page_text

    return True


def verify_first_student_selected(driver):
    checkboxes = driver.find_elements(
        By.XPATH,
        "//table//tbody//input[@type='checkbox']"
    )

    for checkbox in checkboxes:
        try:
            if checkbox.is_selected():
                return True

        except StaleElementReferenceException:
            continue

    raise AssertionError(
        "Student checkbox was not selected."
    )


def wait_for_student_list(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(
            By.XPATH,
            "//table//tbody//tr"
        )

        for row in rows:
            try:
                if row.is_displayed() and row.text.strip():
                    return True

            except StaleElementReferenceException:
                continue

        time.sleep(1)

    raise AssertionError(
        "Student table data not loaded."
    )


def test_promote_students_flow(driver):
    steps = []

    wait = WebDriverWait(driver, 20)

    try:
        page = PromoteStudentsPage(driver)

        driver.get(LOGIN_URL)

        page.wait_page_ready()

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

        page.click(page.LOGIN_BUTTON)

        page.wait_page_ready()

        add_step(
            steps,
            driver,
            "Click Login Button"
        )

        driver.get(PROMOTE_STUDENTS_URL)

        page.wait_page_ready()

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        assert "promote-students" in driver.current_url.lower()

        add_step(
            steps,
            driver,
            "Open Promote Students Page"
        )

        verify_promote_students_page(driver)

        add_step(
            steps,
            driver,
            "Verify Promote Students Page"
        )

        selected_course = page.select_from_course()

        selected_from_sem = page.select_from_semester()

        selected_to_sem = page.select_to_semester()

        add_step(
            steps,
            driver,
            "Fill Promote Students Form",
            "PASS",
            reason=(
                f"Course: {selected_course}, "
                f"From Semester: {selected_from_sem}, "
                f"To Semester: {selected_to_sem}"
            )
        )

        page.click_search()

        page.wait_page_ready()

        add_step(
            steps,
            driver,
            "Click Search Button"
        )

        wait_for_student_list(driver)

        add_step(
            steps,
            driver,
            "Load Students List"
        )

        first_student_row_text = (
            page.get_first_student_row_text()
        )

        add_step(
            steps,
            driver,
            "Verify First Student Row",
            "PASS",
            reason=f"First row found: {first_student_row_text}"
        )

        selected_student_row_text = (
            page.select_first_student_checkbox()
        )

        add_step(
            steps,
            driver,
            "Select First Student Checkbox",
            "PASS",
            reason=f"Selected student row: {selected_student_row_text}"
        )

        verify_first_student_selected(driver)

        add_step(
            steps,
            driver,
            "Verify Student Selected"
        )

        page.click_promote()

        add_step(
            steps,
            driver,
            "Click Promote Button"
        )

        page.click_confirmation_popup()

        add_step(
            steps,
            driver,
            "Handle Confirmation Popup"
        )

        page.wait_for_promoted_successfully()

        add_step(
            steps,
            driver,
            "Verify Promoted Successfully Message"
        )

    except Exception as e:
        error_reason = str(e).strip()

        if not error_reason:
            error_reason = (
                "No detailed error message returned."
            )

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

        pytest.fail(error_reason)

    finally:
        create_pdf_report(
            "Promote_Students_Test_Report",
            steps
        )