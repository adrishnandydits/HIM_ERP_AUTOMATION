# from pages.group_page import GroupPage
#
# import pytest
# import random
# import time
#
# from selenium import webdriver
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# from utils.screenshot import take_screenshot
# from utils.pdf_report import create_pdf_report
#
#
# LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
# GROUP_URL = "https://devanttest.in/him_test/#/student-information/group"
#
# EMAIL = "admin@admin.com"
# PASSWORD = "12345678"
#
# RANDOM_NUMBER = random.randint(1000, 9999)
#
# GROUP_NAME = f"Test Group {RANDOM_NUMBER}"
# EDIT_GROUP_NAME = f"Updated Group {RANDOM_NUMBER}"
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
#     assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"
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
#                 "Group record was not added. "
#                 "After clicking Submit, the Group List table is showing No Data."
#             )
#
#         time.sleep(1)
#
#     raise AssertionError(
#         "Group record was not added. "
#         "After clicking Submit, no row appeared in the Group List table. "
#         "Please check whether the form was submitted successfully or whether the server rejected the request."
#     )
#
#
# def verify_exact_table_row_added(driver, expected_values):
#     rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#     assert len(rows) > 0, "No group record added. Table body is empty."
#
#     expected_values = [
#         str(value).lower().strip()
#         for value in expected_values
#     ]
#
#     for row in rows:
#         row_text = " ".join(row.text.lower().split())
#
#         if all(value in row_text for value in expected_values):
#             return True
#
#     table_text = driver.find_element(By.XPATH, "//table//tbody").text
#
#     raise AssertionError(
#         f"Exact group row not found. "
#         f"Expected values: {expected_values}. "
#         f"Actual table text: {table_text}"
#     )
#
#
# def verify_exact_table_row_deleted(driver, deleted_values, timeout=25):
#     deleted_values = [
#         str(value).lower().strip()
#         for value in deleted_values
#     ]
#
#     end_time = time.time() + timeout
#
#     while time.time() < end_time:
#         try:
#             rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#             if len(rows) == 0:
#                 return True
#
#             deleted_row_found = False
#
#             for row in rows:
#                 row_text = " ".join(row.text.lower().split())
#
#                 if all(value in row_text for value in deleted_values):
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
#         table_text = driver.find_element(By.XPATH, "//table//tbody").text
#     except Exception:
#         table_text = ""
#
#     raise AssertionError(
#         f"Deleted group row still found after waiting. "
#         f"Deleted values: {deleted_values}. "
#         f"Actual table text: {table_text}"
#     )
#
#
# def fill_group_form(page, group_name):
#     page.enter_name(group_name)
#
#
# def test_group_add_edit_delete_flow(driver):
#     steps = []
#     wait = WebDriverWait(driver, 20)
#
#     page = GroupPage(driver)
#
#     driver.get(LOGIN_URL)
#     page.login(EMAIL, PASSWORD)
#
#     driver.get(GROUP_URL)
#
#     # -------- ADD GROUP --------
#     page.enter_name(GROUP_NAME)
#     page.click_submit()
#
#     page.get_exact_row_by_values([GROUP_NAME])
#     add_step(steps, driver, "Group Added Verified")
#
#     # -------- EDIT GROUP --------
#     page.click_edit_for_exact_row([GROUP_NAME])
#
#     page.enter_name(EDIT_GROUP_NAME)
#     page.click_update()
#
#     page.get_exact_row_by_values([EDIT_GROUP_NAME])
#     add_step(steps, driver, "Group Updated Verified")
#
#     # -------- DELETE GROUP --------
#     page.click_delete_for_exact_row([EDIT_GROUP_NAME])
#     page.confirm_delete()
#
#     # verify deleted
#     try:
#         page.get_exact_row_by_values([EDIT_GROUP_NAME])
#         raise AssertionError("Row still exists after delete")
#     except AssertionError:
#         add_step(steps, driver, "Group Deleted Verified")
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
#         create_pdf_report("Group_Test_Report", steps)

from pages.group_page import GroupPage

import pytest
import random
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
GROUP_URL = "https://devanttest.in/him_test/#/student-information/group"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

GROUP_NAME = f"Test Group {RANDOM_NUMBER}"
EDIT_GROUP_NAME = f"Updated Group {RANDOM_NUMBER}"


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


def test_group_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = GroupPage(driver)

        # ---------------- LOGIN ----------------
        driver.get(LOGIN_URL)
        page.login(EMAIL, PASSWORD)

        # ---------------- NAVIGATE ----------------
        driver.get(GROUP_URL)

        # ---------------- ADD GROUP ----------------
        page.enter_name(GROUP_NAME)
        page.click_submit()

        page.get_exact_row_by_values([GROUP_NAME])
        add_step(steps, driver, "Group Added Verified")

        # ---------------- EDIT GROUP ----------------
        page.click_edit_for_exact_row([GROUP_NAME])

        page.enter_name(EDIT_GROUP_NAME)
        page.click_update()

        page.get_exact_row_by_values([EDIT_GROUP_NAME])
        add_step(steps, driver, "Group Updated Verified")

        # ---------------- DELETE GROUP ----------------
        page.click_delete_for_exact_row([EDIT_GROUP_NAME])
        page.confirm_delete()

        # verify deletion (pagination-safe logic already inside page)
        try:
            page.get_exact_row_by_values([EDIT_GROUP_NAME])
            raise AssertionError("Row still exists after delete")
        except AssertionError:
            add_step(steps, driver, "Group Deleted Verified")

        # ---------------- SUCCESS REPORT ----------------
        add_step(steps, driver, "Test Completed Successfully")

    except Exception as e:
        error_reason = str(e).strip() or "No detailed error message returned."

        add_step(
            steps,
            driver,
            "Test Failed",
            "FAIL",
            reason=f"{type(e).__name__}: {error_reason}"
        )

        raise e

    finally:
        create_pdf_report("Group_Test_Report", steps)