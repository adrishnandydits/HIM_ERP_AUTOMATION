# # tests/test_assign_semester_teacher.py
#
# import pytest
#
# from selenium import webdriver
#
# from selenium.webdriver.common.by import By
#
# from selenium.webdriver.support.ui import (
#     WebDriverWait
# )
#
# from selenium.webdriver.support import (
#     expected_conditions as EC
# )
#
# from pages.assign_semester_teacher_page import (
#     AssignSemesterTeacherPage
# )
#
# from utils.screenshot import (
#     take_screenshot
# )
#
# from utils.pdf_report import (
#     create_pdf_report
# )
#
#
# LOGIN_URL = (
#     "https://devanttest.in/him_test/#/auth/login"
# )
#
# ASSIGN_SEMESTER_TEACHER_URL = (
#     "https://devanttest.in/him_test/#/academics/assign-semester-teacher"
# )
#
# EMAIL = "admin@admin.com"
#
# PASSWORD = "12345678"
#
# TEACHER_1 = "Priyanka Adak"
#
# TEACHER_2 = "Bidhan Mondal"
#
#
# @pytest.fixture()
# def driver():
#
#     driver = webdriver.Chrome()
#
#     driver.maximize_window()
#
#     yield driver
#
#     driver.quit()
#
#
# def add_step(
#         steps,
#         driver,
#         name,
#         status="PASS",
#         reason=""
# ):
#
#     image_path = ""
#
#     try:
#
#         image_path = take_screenshot(
#             driver,
#             name.lower().replace(" ", "_")
#         )
#
#     except Exception:
#         image_path = ""
#
#     steps.append({
#
#         "name": name,
#         "status": status,
#         "reason": reason,
#         "image": image_path
#
#     })
#
#
# def verify_assign_semester_teacher_page(
#         driver
# ):
#
#     page_text = " ".join(
#
#         driver.find_element(
#             By.TAG_NAME,
#             "body"
#         ).text.lower().split()
#
#     )
#
#     assert "assign semester teacher" in page_text
#
#     assert "assign teacher" in page_text
#
#     assert "assigned teacher list" in page_text
#
#     assert "select course" in page_text
#
#     assert "select semester" in page_text
#
#     assert "teachers" in page_text
#
#     return True
#
#
# def verify_assigned_teacher_table(
#         driver
# ):
#
#     page_text = " ".join(
#
#         driver.find_element(
#             By.TAG_NAME,
#             "body"
#         ).text.lower().split()
#
#     )
#
#     assert "course name" in page_text
#
#     assert "semester name" in page_text
#
#     assert "teachers assigned" in page_text
#
#     assert "action" in page_text
#
#     return True
#
#
# def test_assign_semester_teacher_flow(
#         driver
# ):
#
#     steps = []
#
#     wait = WebDriverWait(
#         driver,
#         20
#     )
#
#     try:
#
#         page = AssignSemesterTeacherPage(
#             driver
#         )
#
#         driver.get(LOGIN_URL)
#
#         wait.until(
#             EC.presence_of_element_located(
#                 (By.TAG_NAME, "body")
#             )
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Open Login Page"
#         )
#
#         page.enter_text(
#             page.EMAIL,
#             EMAIL
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Enter Email"
#         )
#
#         page.enter_text(
#             page.PASSWORD,
#             PASSWORD
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Enter Password"
#         )
#
#         page.click(
#             page.LOGIN_BUTTON
#         )
#
#         wait.until(
#             EC.presence_of_element_located(
#                 (By.TAG_NAME, "body")
#             )
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Click Login Button"
#         )
#
#         driver.get(
#             ASSIGN_SEMESTER_TEACHER_URL
#         )
#
#         wait.until(
#             EC.presence_of_element_located(
#                 (By.TAG_NAME, "body")
#             )
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Open Assign Semester Teacher Page"
#         )
#
#         verify_assign_semester_teacher_page(
#             driver
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Verify Assign Semester Teacher Page"
#         )
#
#         selected_course = page.select_course()
#
#         add_step(
#             steps,
#             driver,
#             "Select Course",
#             "PASS",
#             reason=f"Selected Course: {selected_course}"
#         )
#
#         selected_semester = page.select_semester()
#
#         add_step(
#             steps,
#             driver,
#             "Select Semester",
#             "PASS",
#             reason=f"Selected Semester: {selected_semester}"
#         )
#
#         page.search_teacher(
#             TEACHER_1
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Search Teacher 1",
#             "PASS",
#             reason=f"Searched Teacher: {TEACHER_1}"
#         )
#
#         selected_teacher_1 = page.select_teacher_chip(
#             TEACHER_1
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Select Teacher 1",
#             "PASS",
#             reason=f"Selected Teacher: {selected_teacher_1}"
#         )
#
#         page.search_teacher(
#             TEACHER_2
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Search Teacher 2",
#             "PASS",
#             reason=f"Searched Teacher: {TEACHER_2}"
#         )
#
#         selected_teacher_2 = page.select_teacher_chip(
#             TEACHER_2
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Select Teacher 2",
#             "PASS",
#             reason=f"Selected Teacher: {selected_teacher_2}"
#         )
#
#         page.click_save()
#
#         add_step(
#             steps,
#             driver,
#             "Click Save Button"
#         )
#
#         page.confirm_save()
#
#         add_step(
#             steps,
#             driver,
#             "Confirm Save"
#         )
#
#         page.wait_for_assigned_teacher_result(
#             [
#                 TEACHER_1,
#                 TEACHER_2
#             ],
#             timeout=40
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Verify Assigned Teachers Added"
#         )
#
#         verify_assigned_teacher_table(
#             driver
#         )
#
#         add_step(
#             steps,
#             driver,
#             "Verify Assigned Teacher Table"
#         )
#
#     except Exception as e:
#
#         error_reason = str(e).strip()
#
#         if not error_reason:
#
#             error_reason = (
#                 "No detailed error message returned."
#             )
#
#         error_reason = (
#             f"{type(e).__name__}: {error_reason}"
#         )
#
#         try:
#
#             add_step(
#                 steps,
#                 driver,
#                 "Test Failed",
#                 "FAIL",
#                 reason=error_reason
#             )
#
#         except Exception:
#
#             steps.append({
#
#                 "name": "Test Failed",
#                 "status": "FAIL",
#                 "reason": error_reason,
#                 "image": ""
#
#             })
#
#         raise e
#
#     finally:
#
#         create_pdf_report(
#             "Assign_Semester_Teacher_Report",
#             steps
#         )


import pytest

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import (
    WebDriverWait
)

from selenium.webdriver.support import (
    expected_conditions as EC
)

from pages.assign_semester_teacher_page import (
    AssignSemesterTeacherPage
)

from utils.screenshot import (
    take_screenshot
)

from utils.pdf_report import (
    create_pdf_report
)


LOGIN_URL = (
    "https://devanttest.in/him_test/#/auth/login"
)

ASSIGN_SEMESTER_TEACHER_URL = (
    "https://devanttest.in/him_test/#/academics/assign-semester-teacher"
)

EMAIL = "admin@admin.com"

PASSWORD = "12345678"

TEACHER_1 = "Priyanka Adak"

TEACHER_2 = "Bidhan Mondal"

UPDATED_TEACHER = "Sourav Das"


@pytest.fixture()
def driver():

    driver = webdriver.Chrome()

    driver.maximize_window()

    yield driver

    driver.quit()


def add_step(
        steps,
        driver,
        name,
        status="PASS",
        reason=""
):

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


def test_assign_semester_teacher_flow(
        driver
):

    steps = []

    wait = WebDriverWait(
        driver,
        20
    )

    try:

        page = AssignSemesterTeacherPage(
            driver
        )

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

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

        page.enter_text(
            page.PASSWORD,
            PASSWORD
        )

        add_step(
            steps,
            driver,
            "Enter Login Credentials"
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
            "Login Successful"
        )

        # -------------------------------------------------
        # OPEN PAGE
        # -------------------------------------------------

        driver.get(
            ASSIGN_SEMESTER_TEACHER_URL
        )

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        add_step(
            steps,
            driver,
            "Open Assign Semester Teacher Page"
        )

        # -------------------------------------------------
        # CREATE FLOW
        # -------------------------------------------------

        selected_course = page.select_course()

        add_step(
            steps,
            driver,
            "Select Course",
            reason=f"Selected Course: {selected_course}"
        )

        selected_semester = page.select_semester()

        add_step(
            steps,
            driver,
            "Select Semester",
            reason=f"Selected Semester: {selected_semester}"
        )

        page.search_teacher(
            TEACHER_1
        )

        page.select_teacher_chip(
            TEACHER_1
        )

        add_step(
            steps,
            driver,
            "Assign Teacher 1",
            reason=f"Teacher: {TEACHER_1}"
        )

        page.search_teacher(
            TEACHER_2
        )

        page.select_teacher_chip(
            TEACHER_2
        )

        add_step(
            steps,
            driver,
            "Assign Teacher 2",
            reason=f"Teacher: {TEACHER_2}"
        )

        page.click_save()

        add_step(
            steps,
            driver,
            "Click Save Button"
        )

        page.confirm_save()

        add_step(
            steps,
            driver,
            "Confirm Save"
        )

        # -------------------------------------------------
        # PAGINATION
        # -------------------------------------------------

        page.scroll_to_bottom()

        add_step(
            steps,
            driver,
            "Scroll To Bottom"
        )

        page.click_next_pagination()

        add_step(
            steps,
            driver,
            "Open Next Pagination"
        )

        # -------------------------------------------------
        # VERIFY CREATED RECORD
        # -------------------------------------------------

        page.verify_recent_teacher_record(
            TEACHER_1
        )

        add_step(
            steps,
            driver,
            "Verify Created Record"
        )

        # -------------------------------------------------
        # EDIT FLOW
        # -------------------------------------------------

        page.click_edit_button()

        add_step(
            steps,
            driver,
            "Click Edit Button"
        )

        page.update_teacher(
            TEACHER_2,
            UPDATED_TEACHER
        )

        add_step(
            steps,
            driver,
            "Update Teacher",
            reason=(
                f"{TEACHER_2} replaced with "
                f"{UPDATED_TEACHER}"
            )
        )

        page.click_save()

        add_step(
            steps,
            driver,
            "Save Updated Record"
        )

        page.confirm_save()

        add_step(
            steps,
            driver,
            "Confirm Updated Save"
        )

        # -------------------------------------------------
        # VERIFY UPDATED RECORD
        # -------------------------------------------------

        page.scroll_to_bottom()

        page.click_next_pagination()

        page.verify_recent_teacher_record(
            UPDATED_TEACHER
        )

        add_step(
            steps,
            driver,
            "Verify Updated Record"
        )

        # -------------------------------------------------
        # DELETE FLOW
        # -------------------------------------------------

        page.click_delete_button()

        add_step(
            steps,
            driver,
            "Click Delete Button"
        )

        page.confirm_delete()

        add_step(
            steps,
            driver,
            "Confirm Delete"
        )

        # -------------------------------------------------
        # VERIFY DELETED RECORD
        # -------------------------------------------------

        time.sleep(3)

        page.verify_teacher_deleted(
            UPDATED_TEACHER
        )

        add_step(
            steps,
            driver,
            "Verify Record Deleted"
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

        raise e

    finally:

        create_pdf_report(
            "Assign_Semester_Teacher_Test_Report",
            steps
        )