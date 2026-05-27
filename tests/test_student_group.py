#
#
# from pages.student_group_page import StudentGroupPage
#
# import pytest
# import time
#
# from selenium import webdriver
# from selenium.common.exceptions import (
#     StaleElementReferenceException,
#     TimeoutException
# )
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# from utils.screenshot import take_screenshot
# from utils.pdf_report import create_pdf_report
#
#
# LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
# STUDENT_GROUP_URL = "https://devanttest.in/him_test/#/student-information/student-group"
#
# EMAIL = "admin@admin.com"
# PASSWORD = "12345678"
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
#     visible_errors = [
#         error.text.strip()
#         for error in errors
#         if error.is_displayed() and error.text.strip()
#     ]
#
#     assert len(visible_errors) == 0, (
#         f"Validation error found: {visible_errors}"
#     )
#
#
# def wait_for_table_or_validation(driver, timeout=25):
#     end_time = time.time() + timeout
#
#     while time.time() < end_time:
#         rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#         if len(rows) > 0:
#             return True
#
#         errors = driver.find_elements(
#             By.XPATH,
#             "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
#         )
#
#         visible_errors = [
#             error.text.strip()
#             for error in errors
#             if error.is_displayed() and error.text.strip()
#         ]
#
#         if visible_errors:
#             raise AssertionError(
#                 f"Validation error found after submit: {visible_errors}"
#             )
#
#         no_data = driver.find_elements(
#             By.XPATH,
#             "//*[contains(normalize-space(),'No Data') or contains(normalize-space(),'No Record') or contains(normalize-space(),'No records')]"
#         )
#
#         if any(element.is_displayed() for element in no_data):
#             raise AssertionError(
#                 "Student group record was not added. "
#                 "After clicking Submit, the Subject Group table is showing No Data."
#             )
#
#         time.sleep(1)
#
#     raise AssertionError(
#         "Student group record was not added. "
#         "After clicking Submit, no row appeared in the Subject Group table."
#     )
#
#
# def normalize_text(value):
#     return " ".join(str(value).lower().split()).strip()
#
#
# def verify_exact_table_row_added(driver, expected_values):
#     rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#     assert len(rows) > 0, (
#         "No student group record added. Table body is empty."
#     )
#
#     expected_values = [
#         normalize_text(value)
#         for value in expected_values
#     ]
#
#     for row in rows:
#         row_text = normalize_text(row.text)
#
#         matched_values = [
#             value
#             for value in expected_values
#             if value in row_text
#         ]
#
#         if len(matched_values) == len(expected_values):
#             return True
#
#     table_text = ""
#
#     try:
#         table_text = driver.find_element(
#             By.XPATH,
#             "//table//tbody"
#         ).text
#     except Exception:
#         table_text = driver.find_element(
#             By.XPATH,
#             "//body"
#         ).text
#
#     raise AssertionError(
#         f"Exact student group row not found.\n\n"
#         f"Expected values:\n{expected_values}\n\n"
#         f"Actual table text:\n{table_text}"
#     )
#
#
# def verify_exact_table_row_deleted(
#         driver,
#         deleted_values,
#         timeout=25
# ):
#     deleted_values = [
#         normalize_text(value)
#         for value in deleted_values
#     ]
#
#     end_time = time.time() + timeout
#
#     while time.time() < end_time:
#         try:
#             rows = driver.find_elements(
#                 By.XPATH,
#                 "//table//tbody//tr"
#             )
#
#             if len(rows) == 0:
#                 return True
#
#             deleted_row_found = False
#
#             for row in rows:
#                 row_text = normalize_text(row.text)
#
#                 if all(
#                         value in row_text
#                         for value in deleted_values
#                 ):
#                     deleted_row_found = True
#                     break
#
#             if not deleted_row_found:
#                 return True
#
#         except StaleElementReferenceException:
#             return True
#
#         time.sleep(1)
#
#     table_text = ""
#
#     try:
#         table_text = driver.find_element(
#             By.XPATH,
#             "//table//tbody"
#         ).text
#     except Exception:
#         table_text = ""
#
#     raise AssertionError(
#         f"Deleted student group row still found after waiting.\n\n"
#         f"Deleted values:\n{deleted_values}\n\n"
#         f"Actual table text:\n{table_text}"
#     )
#
#
# def clear_search_filter(page):
#     try:
#         page.enter_search_or_filter("")
#         time.sleep(2)
#     except Exception:
#         pass
#
#
# def fill_student_group_form(page):
#     selected_course = page.select_course()
#
#     selected_semester = page.select_semester()
#
#     selected_group = page.select_group()
#
#     selected_student = page.get_first_student_name()
#
#     page.click_first_student_checkbox()
#
#     return (
#         selected_course,
#         selected_semester,
#         selected_group,
#         selected_student
#     )
#
#
# def test_student_group_add_edit_delete_flow(driver):
#     steps = []
#
#     wait = WebDriverWait(driver, 20)
#
#     try:
#         page = StudentGroupPage(driver)
#
#         driver.get(LOGIN_URL)
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         add_step(steps, driver, "Open Login Page")
#
#         page.enter_text(page.EMAIL, EMAIL)
#
#         add_step(steps, driver, "Enter Email")
#
#         page.enter_text(page.PASSWORD, PASSWORD)
#
#         add_step(steps, driver, "Enter Password")
#
#         page.click(page.LOGIN_BUTTON)
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         add_step(steps, driver, "Click Login Button")
#
#         driver.get(STUDENT_GROUP_URL)
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         assert "student-group" in driver.current_url.lower()
#
#         add_step(steps, driver, "Open Student Group Page")
#
#         (
#             SELECTED_COURSE,
#             SELECTED_SEMESTER,
#             SELECTED_GROUP,
#             SELECTED_STUDENT
#         ) = fill_student_group_form(page)
#
#         add_step(
#             steps,
#             driver,
#             "Fill Student Group Form And Select Student"
#         )
#
#         page.click_submit()
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         add_step(steps, driver, "Click Submit Button")
#         time.sleep(20)
#
#         verify_no_validation_error(driver)
#
#         wait_for_table_or_validation(driver, timeout=25)
#
#         add_step(steps, driver, "Load Subject Group List")
#
#         page.enter_search_or_filter(SELECTED_GROUP)
#
#         time.sleep(2)
#
#         add_step(steps, driver, "Search Added Group")
#
#         ADDED_ROW_VALUES = [
#             SELECTED_SEMESTER,
#             SELECTED_GROUP,
#             SELECTED_STUDENT
#         ]
#
#         verify_exact_table_row_added(
#             driver,
#             ADDED_ROW_VALUES
#         )
#
#         add_step(steps, driver, "Verify Student Group Added")
#
#         time.sleep(30)
#
#         page.click_edit_for_exact_row(
#             [
#                 SELECTED_GROUP,
#                 SELECTED_STUDENT
#             ]
#         )
#
#         wait.until(
#             EC.presence_of_element_located(page.GROUP)
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Click Edit Button For Exact Added Row"
#         )
#
#         EDIT_SELECTED_GROUP = page.select_edit_group()
#
#         EDIT_SELECTED_STUDENT = page.get_first_student_name()
#
#         page.click_first_student_checkbox()
#
#         add_step(
#             steps,
#             driver,
#             "Edit Student Group Form And Select Student"
#         )
#
#         page.click_update()
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         add_step(steps, driver, "Click Update Button")
#
#         verify_no_validation_error(driver)
#
#         wait_for_table_or_validation(driver, timeout=25)
#
#         add_step(
#             steps,
#             driver,
#             "Load Updated Subject Group List"
#         )
#
#         clear_search_filter(page)
#
#         page.enter_search_or_filter(EDIT_SELECTED_GROUP)
#
#         time.sleep(2)
#
#         add_step(steps, driver, "Search Updated Group")
#
#         UPDATED_ROW_VALUES = [
#             SELECTED_SEMESTER,
#             EDIT_SELECTED_GROUP,
#             EDIT_SELECTED_STUDENT
#         ]
#
#         verify_exact_table_row_added(
#             driver,
#             UPDATED_ROW_VALUES
#         )
#
#         add_step(steps, driver, "Verify Student Group Updated")
#
#         page.click_delete_for_exact_row(
#             [
#                 EDIT_SELECTED_GROUP,
#                 EDIT_SELECTED_STUDENT
#             ]
#         )
#
#         delete_confirm_buttons = driver.find_elements(
#             By.XPATH,
#             "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
#         )
#
#         assert len(delete_confirm_buttons) > 0, (
#             "Delete confirmation popup did not appear after clicking delete button."
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Click Delete Button For Exact Updated Row"
#         )
#
#         page.confirm_delete()
#
#         wait.until(
#             EC.presence_of_element_located((By.XPATH, "//body"))
#         )
#
#         time.sleep(2)
#
#         add_step(steps, driver, "Confirm Delete")
#
#         verify_exact_table_row_deleted(
#             driver,
#             [
#                 EDIT_SELECTED_GROUP,
#                 EDIT_SELECTED_STUDENT
#             ],
#             timeout=25
#         )
#
#         add_step(steps, driver, "Verify Student Group Deleted")
#
#     except Exception as e:
#         error_reason = str(e).strip()
#
#         if not error_reason:
#             error_reason = (
#                 "No detailed error message returned by Selenium."
#             )
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
#         create_pdf_report(
#             "Student_Group_Test_Report",
#             steps
#         )


from pages.student_group_page import StudentGroupPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
STUDENT_GROUP_URL = "https://devanttest.in/him_test/#/student-information/student-group"

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

    assert len(visible_errors) == 0, (
        f"Validation error found: {visible_errors}"
    )


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
                "Student group record was not added. "
                "After clicking Submit, the Subject Group table is showing No Data."
            )

        time.sleep(1)

    raise AssertionError(
        "Student group record was not added. "
        "After clicking Submit, no row appeared in the Subject Group table."
    )


def normalize_text(value):
    return " ".join(str(value).lower().split()).strip()


# UPDATED WITH PAGINATION SUPPORT
def verify_exact_table_row_added(
        driver,
        expected_values,
        page,
        timeout=40
):
    expected_values = [
        normalize_text(value)
        for value in expected_values
    ]

    end_time = time.time() + timeout
    checked_pages = 0

    while time.time() < end_time and checked_pages < 50:
        rows = driver.find_elements(
            By.XPATH,
            "//table//tbody//tr"
        )

        for row in rows:
            row_text = normalize_text(row.text)

            matched_values = [
                value
                for value in expected_values
                if value in row_text
            ]

            if len(matched_values) == len(expected_values):
                return True

        # GO NEXT PAGE
        try:
            next_btn = driver.find_element(
                *page.NEXT_PAGE_BUTTON
            )

            parent_class = next_btn.find_element(
                By.XPATH,
                "./parent::*"
            ).get_attribute("class").lower()

            if "disabled" in parent_class:
                break

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                next_btn
            )

            try:
                next_btn.click()
            except Exception:
                driver.execute_script(
                    "arguments[0].click();",
                    next_btn
                )

            time.sleep(2)
            checked_pages += 1

        except Exception:
            break

    table_text = ""

    try:
        table_text = driver.find_element(
            By.XPATH,
            "//table//tbody"
        ).text
    except Exception:
        table_text = driver.find_element(
            By.XPATH,
            "//body"
        ).text

    raise AssertionError(
        f"Exact student group row not found across pagination.\n\n"
        f"Expected values:\n{expected_values}\n\n"
        f"Actual table text:\n{table_text}"
    )


# UPDATED WITH PAGINATION SUPPORT
def verify_exact_table_row_deleted(
        driver,
        deleted_values,
        page,
        timeout=40
):
    deleted_values = [
        normalize_text(value)
        for value in deleted_values
    ]

    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            checked_pages = 0
            deleted_row_found = False

            while checked_pages < 50:
                rows = driver.find_elements(
                    By.XPATH,
                    "//table//tbody//tr"
                )

                for row in rows:
                    row_text = normalize_text(row.text)

                    if all(
                            value in row_text
                            for value in deleted_values
                    ):
                        deleted_row_found = True
                        break

                if deleted_row_found:
                    break

                try:
                    next_btn = driver.find_element(
                        *page.NEXT_PAGE_BUTTON
                    )

                    parent_class = next_btn.find_element(
                        By.XPATH,
                        "./parent::*"
                    ).get_attribute("class").lower()

                    if "disabled" in parent_class:
                        break

                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        next_btn
                    )

                    try:
                        next_btn.click()
                    except Exception:
                        driver.execute_script(
                            "arguments[0].click();",
                            next_btn
                        )

                    time.sleep(2)
                    checked_pages += 1

                except Exception:
                    break

            if not deleted_row_found:
                return True

        except StaleElementReferenceException:
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(
            By.XPATH,
            "//table//tbody"
        ).text
    except Exception:
        table_text = ""

    raise AssertionError(
        f"Deleted student group row still found after waiting.\n\n"
        f"Deleted values:\n{deleted_values}\n\n"
        f"Actual table text:\n{table_text}"
    )


def clear_search_filter(page):
    try:
        page.enter_search_or_filter("")
        time.sleep(2)
    except Exception:
        pass


def fill_student_group_form(page):
    selected_course = page.select_course()

    selected_semester = page.select_semester()

    selected_group = page.select_group()

    selected_student = page.get_first_student_name()

    page.click_first_student_checkbox()

    return (
        selected_course,
        selected_semester,
        selected_group,
        selected_student
    )


def test_student_group_add_edit_delete_flow(driver):
    steps = []

    wait = WebDriverWait(driver, 20)

    try:
        page = StudentGroupPage(driver)

        driver.get(LOGIN_URL)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        add_step(steps, driver, "Open Login Page")

        page.enter_text(page.EMAIL, EMAIL)

        add_step(steps, driver, "Enter Email")

        page.enter_text(page.PASSWORD, PASSWORD)

        add_step(steps, driver, "Enter Password")

        page.click(page.LOGIN_BUTTON)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        add_step(steps, driver, "Click Login Button")

        driver.get(STUDENT_GROUP_URL)

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        assert "student-group" in driver.current_url.lower()

        add_step(steps, driver, "Open Student Group Page")

        (
            SELECTED_COURSE,
            SELECTED_SEMESTER,
            SELECTED_GROUP,
            SELECTED_STUDENT
        ) = fill_student_group_form(page)

        add_step(
            steps,
            driver,
            "Fill Student Group Form And Select Student"
        )

        page.click_submit()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        add_step(steps, driver, "Click Submit Button")

        time.sleep(20)

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)

        add_step(steps, driver, "Load Subject Group List")

        clear_search_filter(page)

        page.enter_search_or_filter(SELECTED_GROUP)

        time.sleep(3)

        add_step(steps, driver, "Search Added Group")

        ADDED_ROW_VALUES = [
            SELECTED_SEMESTER,
            SELECTED_GROUP,
            SELECTED_STUDENT
        ]

        verify_exact_table_row_added(
            driver,
            ADDED_ROW_VALUES,
            page
        )

        add_step(steps, driver, "Verify Student Group Added")

        time.sleep(3)

        page.click_edit_for_exact_row(
            [
                SELECTED_GROUP,
                SELECTED_STUDENT
            ]
        )

        wait.until(
            EC.presence_of_element_located(page.GROUP)
        )

        add_step(
            steps,
            driver,
            "Click Edit Button For Exact Added Row"
        )

        EDIT_SELECTED_GROUP = page.select_edit_group()

        # # UNCHECK OLD STUDENT
        # page.uncheck_selected_student_if_checked()
        #
        # # GET NEW STUDENT
        # EDIT_SELECTED_STUDENT = (
        #     page.get_first_unchecked_student_name()
        # )
        #
        # # SELECT NEW STUDENT
        # page.click_first_unchecked_student_checkbox()

        OLD_SELECTED_STUDENT = (
            page.uncheck_selected_student_if_checked()
        )

        time.sleep(2)

        EDIT_SELECTED_STUDENT = (
            page.click_first_unchecked_student_checkbox(
                OLD_SELECTED_STUDENT
            )
        )

        assert (
                EDIT_SELECTED_STUDENT.lower()
                != OLD_SELECTED_STUDENT.lower()
        ), (
            "Same student got selected again during edit."
        )

        add_step(
            steps,
            driver,
            "Edit Student Group Form And Select New Student"
        )

        page.click_update()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        add_step(
            steps,
            driver,
            "Click Update Button"
        )

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=25)

        add_step(
            steps,
            driver,
            "Load Updated Subject Group List"
        )

        clear_search_filter(page)

        page.enter_search_or_filter(EDIT_SELECTED_GROUP)

        time.sleep(3)

        add_step(steps, driver, "Search Updated Group")

        UPDATED_ROW_VALUES = [
            SELECTED_SEMESTER,
            EDIT_SELECTED_GROUP,
            EDIT_SELECTED_STUDENT
        ]

        verify_exact_table_row_added(
            driver,
            UPDATED_ROW_VALUES,
            page
        )

        add_step(steps, driver, "Verify Student Group Updated")

        # PAGINATION-AWARE DELETE
        page.click_delete_for_exact_row(
            [
                EDIT_SELECTED_GROUP,
                EDIT_SELECTED_STUDENT
            ]
        )

        delete_confirm_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
        )

        assert len(delete_confirm_buttons) > 0, (
            "Delete confirmation popup did not appear after clicking delete button."
        )

        add_step(
            steps,
            driver,
            "Click Delete Button For Exact Updated Row"
        )

        page.confirm_delete()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        time.sleep(3)

        add_step(steps, driver, "Confirm Delete")

        clear_search_filter(page)

        page.enter_search_or_filter(EDIT_SELECTED_GROUP)

        time.sleep(3)

        verify_exact_table_row_deleted(
            driver,
            [
                EDIT_SELECTED_GROUP,
                EDIT_SELECTED_STUDENT
            ],
            page,
            timeout=40
        )

        add_step(steps, driver, "Verify Student Group Deleted")

    except Exception as e:
        error_reason = str(e).strip()

        if not error_reason:
            error_reason = (
                "No detailed error message returned by Selenium."
            )

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
        create_pdf_report(
            "Student_Group_Test_Report",
            steps
        )
