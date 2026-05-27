# import time
#
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
#
#
# class PromoteStudentsPage:
#     EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
#     PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
#     LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")
#
#     FROM_COURSE = (
#         By.XPATH,
#         "(//label[contains(normalize-space(),'Course')]/following::select[1])[1]"
#     )
#
#     FROM_SEMESTER = (
#         By.XPATH,
#         "(//label[contains(normalize-space(),'Semester')]/following::select[1])[1]"
#     )
#
#     TO_SEMESTER = (
#         By.XPATH,
#         "(//label[contains(normalize-space(),'Semester')]/following::select[1])[2]"
#     )
#
#     SEARCH_BUTTON = (
#         By.XPATH,
#         "//button[contains(normalize-space(),'Search')]"
#     )
#
#     PROMOTE_BUTTON = (
#         By.XPATH,
#         "//button[contains(normalize-space(),'Promote')]"
#     )
#
#     SEARCH_OR_FILTER = (
#         By.XPATH,
#         "//input[contains(@placeholder,'Search') or contains(@placeholder,'Filter')]"
#     )
#
#     STUDENT_TABLE = (
#         By.XPATH,
#         "//table"
#     )
#
#     SUCCESS_POPUP = (
#         By.XPATH,
#         "//*[contains(normalize-space(),'Promoted Successfully') or contains(normalize-space(),'promoted successfully')]"
#     )
#
#     def __init__(self, driver, timeout=20):
#         self.driver = driver
#         self.wait = WebDriverWait(driver, timeout)
#
#     def scroll(self, locator):
#         element = self.wait.until(EC.presence_of_element_located(locator))
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             element
#         )
#
#         time.sleep(0.5)
#         return element
#
#     def click(self, locator):
#         element = self.scroll(locator)
#
#         try:
#             self.wait.until(EC.element_to_be_clickable(locator))
#             element.click()
#         except Exception:
#             self.driver.execute_script("arguments[0].click();", element)
#
#         time.sleep(1.2)
#
#     def enter_text(self, locator, text):
#         element = self.scroll(locator)
#         element.clear()
#         element.send_keys(text)
#         time.sleep(0.7)
#
#     def select_by_visible_text(self, locator, visible_text):
#         element = self.scroll(locator)
#
#         try:
#             Select(element).select_by_visible_text(visible_text)
#         except Exception:
#             self.driver.execute_script("arguments[0].click();", element)
#
#             option = (
#                 By.XPATH,
#                 f"//option[contains(normalize-space(),'{visible_text}')]"
#             )
#
#             option_element = self.wait.until(
#                 EC.element_to_be_clickable(option)
#             )
#
#             option_element.click()
#
#         self.driver.execute_script(
#             """
#             arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
#             arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
#             arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
#             """,
#             element
#         )
#
#         time.sleep(1.5)
#
#     def select_first_valid_option(self, locator, field_name, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             element = self.scroll(locator)
#             select = Select(element)
#
#             valid_options = [
#                 option
#                 for option in select.options
#                 if option.text.strip()
#                 and option.text.strip().lower() not in [
#                     "select",
#                     "--select--",
#                     "-select-",
#                     "--select",
#                     "select course",
#                     "select semester"
#                 ]
#             ]
#
#             if len(valid_options) > 0:
#                 selected_text = valid_options[0].text.strip()
#                 select.select_by_visible_text(selected_text)
#
#                 self.driver.execute_script(
#                     """
#                     arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
#                     arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
#                     arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
#                     """,
#                     element
#                 )
#
#                 time.sleep(1.5)
#                 return selected_text
#
#             time.sleep(1)
#
#         raise AssertionError(
#             f"No valid {field_name} option found after waiting {timeout} seconds."
#         )
#
#     def wait_for_from_semester_options(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             element = self.scroll(self.FROM_SEMESTER)
#             select = Select(element)
#
#             valid_options = [
#                 option.text.strip()
#                 for option in select.options
#                 if option.text.strip()
#                 and option.text.strip().lower() not in [
#                     "select",
#                     "--select--",
#                     "-select-",
#                     "select semester"
#                 ]
#             ]
#
#             if len(valid_options) > 0:
#                 return True
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "From Semester dropdown options did not load after selecting course."
#         )
#
#     def wait_for_to_semester_options(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             element = self.scroll(self.TO_SEMESTER)
#             select = Select(element)
#
#             valid_options = [
#                 option.text.strip()
#                 for option in select.options
#                 if option.text.strip()
#                 and option.text.strip().lower() not in [
#                     "select",
#                     "--select--",
#                     "-select-",
#                     "select semester"
#                 ]
#             ]
#
#             if len(valid_options) > 0:
#                 return True
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "To Semester dropdown options did not load."
#         )
#
#     def select_from_course(self):
#         try:
#             self.select_by_visible_text(self.FROM_COURSE, "BBA (ACCOUNTANCY, TAXATION & AUDITING)")
#             return "BBA (ACCOUNTANCY, TAXATION & AUDITING)"
#         except Exception:
#             return self.select_first_valid_option(
#                 self.FROM_COURSE,
#                 "from course",
#                 timeout=25
#             )
#
#     def select_from_semester(self):
#         self.wait_for_from_semester_options(timeout=25)
#
#         try:
#             self.select_by_visible_text(self.FROM_SEMESTER, "3rd Sem")
#             return "3rd Sem"
#         except Exception:
#             return self.select_first_valid_option(
#                 self.FROM_SEMESTER,
#                 "from semester",
#                 timeout=25
#             )
#
#     def select_to_semester(self):
#         self.wait_for_to_semester_options(timeout=25)
#
#         try:
#             self.select_by_visible_text(self.TO_SEMESTER, "4th Sem")
#             return "4th Sem"
#         except Exception:
#             return self.select_first_valid_option(
#                 self.TO_SEMESTER,
#                 "to semester",
#                 timeout=25
#             )
#
#     def click_search(self):
#         self.click(self.SEARCH_BUTTON)
#
#     def click_promote(self):
#         self.click(self.PROMOTE_BUTTON)
#
#     def wait_for_student_table(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             try:
#                 tables = self.driver.find_elements(By.XPATH, "//table")
#
#                 if len(tables) > 0:
#                     rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#                     visible_rows = []
#
#                     for row in rows:
#                         try:
#                             if row.is_displayed() and row.text.strip():
#                                 visible_rows.append(row)
#                         except StaleElementReferenceException:
#                             continue
#
#                     if len(visible_rows) > 0:
#                         return True
#
#                 no_data_elements = self.driver.find_elements(
#                     By.XPATH,
#                     "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
#                     "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
#                     "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'not found')]"
#                 )
#
#                 visible_no_data = []
#
#                 for element in no_data_elements:
#                     try:
#                         if element.is_displayed() and element.text.strip():
#                             visible_no_data.append(element.text.strip())
#                     except StaleElementReferenceException:
#                         continue
#
#                 if visible_no_data:
#                     raise AssertionError(
#                         f"No student data found after search. Message shown: {visible_no_data}"
#                     )
#
#             except StaleElementReferenceException:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "Student table did not load after clicking Search."
#         )
#
#     def get_first_student_row_text(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             try:
#                 rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#                 for row in rows:
#                     if row.is_displayed() and row.text.strip():
#                         return " ".join(row.text.split())
#
#             except StaleElementReferenceException:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError("No stable student row text was found.")
#
#     def select_first_student_checkbox(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             try:
#                 rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#                 for row in rows:
#                     if not row.is_displayed() or not row.text.strip():
#                         continue
#
#                     checkboxes = row.find_elements(
#                         By.XPATH,
#                         ".//input[@type='checkbox']"
#                     )
#
#                     if len(checkboxes) == 0:
#                         continue
#
#                     checkbox = checkboxes[0]
#
#                     self.driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});",
#                         checkbox
#                     )
#
#                     if not checkbox.is_selected():
#                         try:
#                             checkbox.click()
#                         except Exception:
#                             self.driver.execute_script("arguments[0].click();", checkbox)
#
#                     time.sleep(1)
#                     return " ".join(row.text.split())
#
#             except StaleElementReferenceException:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "First student checkbox was not found."
#         )
#
#     def select_check_all(self):
#         check_all = self.wait.until(
#             EC.presence_of_element_located(
#                 (
#                     By.XPATH,
#                     "//table//thead//input[@type='checkbox']"
#                 )
#             )
#         )
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             check_all
#         )
#
#         if not check_all.is_selected():
#             try:
#                 check_all.click()
#             except Exception:
#                 self.driver.execute_script("arguments[0].click();", check_all)
#
#         time.sleep(1)
#
#     def wait_for_promoted_successfully(self, timeout=30):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             success_messages = self.driver.find_elements(
#                 By.XPATH,
#                 "//*[contains(normalize-space(),'Promoted Successfully') or contains(normalize-space(),'promoted successfully')]"
#             )
#
#             visible_success = []
#
#             for message in success_messages:
#                 try:
#                     if message.is_displayed():
#                         visible_success.append(message)
#                 except StaleElementReferenceException:
#                     continue
#
#             if len(visible_success) > 0:
#                 return True
#
#             errors = self.driver.find_elements(
#                 By.XPATH,
#                 "//*[contains(text(),'failed') or contains(text(),'Failed') or contains(text(),'error') or contains(text(),'Error')]"
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
#                     f"Error found while promoting student: {visible_errors}"
#                 )
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "Promoted Successfully popup was not shown after clicking Promote."
#         )

import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class PromoteStudentsPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    FROM_COURSE = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Course')]/following::select[1])[1]"
    )

    FROM_SEMESTER = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Semester')]/following::select[1])[1]"
    )

    TO_SEMESTER = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Semester')]/following::select[1])[2]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
    )

    PROMOTE_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Promote')]"
    )

    CONFIRM_BUTTON = (
        By.XPATH,
        "//button[contains(.,'Yes') "
        "or contains(.,'YES') "
        "or contains(.,'Ok') "
        "or contains(.,'OK') "
        "or contains(.,'Confirm')]"
    )

    SUCCESS_POPUP = (
        By.XPATH,
        "//*[contains(translate(normalize-space(), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "'abcdefghijklmnopqrstuvwxyz'), "
        "'promot')]"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_page_ready(self):
        self.wait.until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

    def scroll(self, locator):
        element = self.wait.until(
            EC.presence_of_element_located(locator)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        time.sleep(0.5)

        return element

    def click(self, locator):
        element = self.wait.until(
            EC.element_to_be_clickable(locator)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        try:
            element.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

        time.sleep(1.5)

    def enter_text(self, locator, text):
        element = self.scroll(locator)

        element.clear()
        element.send_keys(text)

        time.sleep(1)

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        try:
            Select(element).select_by_visible_text(visible_text)

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

            option = (
                By.XPATH,
                f"//option[contains(normalize-space(),'{visible_text}')]"
            )

            option_element = self.wait.until(
                EC.element_to_be_clickable(option)
            )

            option_element.click()

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(2)

    def select_first_valid_option(self, locator, field_name, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            element = self.scroll(locator)

            select = Select(element)

            valid_options = [
                option
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "--select--",
                    "-select-",
                    "--select",
                    "select course",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                selected_text = valid_options[0].text.strip()

                select.select_by_visible_text(selected_text)

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                    """,
                    element
                )

                time.sleep(2)

                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found."
        )

    def wait_for_from_semester_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            element = self.scroll(self.FROM_SEMESTER)

            select = Select(element)

            valid_options = [
                option.text.strip()
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "--select--",
                    "-select-",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "From Semester options not loaded."
        )

    def wait_for_to_semester_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            element = self.scroll(self.TO_SEMESTER)

            select = Select(element)

            valid_options = [
                option.text.strip()
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "--select--",
                    "-select-",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "To Semester options not loaded."
        )

    def select_from_course(self):
        try:
            self.select_by_visible_text(
                self.FROM_COURSE,
                "BBA (ACCOUNTANCY, TAXATION & AUDITING)"
            )

            return "BBA (ACCOUNTANCY, TAXATION & AUDITING)"

        except Exception:
            return self.select_first_valid_option(
                self.FROM_COURSE,
                "from course"
            )

    def select_from_semester(self):
        self.wait_for_from_semester_options()

        try:
            self.select_by_visible_text(
                self.FROM_SEMESTER,
                "3rd Sem"
            )

            return "3rd Sem"

        except Exception:
            return self.select_first_valid_option(
                self.FROM_SEMESTER,
                "from semester"
            )

    def select_to_semester(self):
        self.wait_for_to_semester_options()

        try:
            self.select_by_visible_text(
                self.TO_SEMESTER,
                "4th Sem"
            )

            return "4th Sem"

        except Exception:
            return self.select_first_valid_option(
                self.TO_SEMESTER,
                "to semester"
            )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def click_promote(self):
        self.click(self.PROMOTE_BUTTON)

    def click_confirmation_popup(self, timeout=10):
        try:
            confirm_button = WebDriverWait(
                self.driver,
                timeout
            ).until(
                EC.element_to_be_clickable(
                    self.CONFIRM_BUTTON
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                confirm_button
            )

            try:
                confirm_button.click()

            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    confirm_button
                )

            time.sleep(2)

            return True

        except TimeoutException:
            return False

    def get_first_student_row_text(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(
                    By.XPATH,
                    "//table//tbody//tr"
                )

                for row in rows:
                    if row.is_displayed() and row.text.strip():
                        return " ".join(row.text.split())

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            "No student row found."
        )

    def select_first_student_checkbox(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(
                    By.XPATH,
                    "//table//tbody//tr"
                )

                for row in rows:
                    if not row.is_displayed():
                        continue

                    if not row.text.strip():
                        continue

                    checkboxes = row.find_elements(
                        By.XPATH,
                        ".//input[@type='checkbox']"
                    )

                    if len(checkboxes) == 0:
                        continue

                    checkbox = checkboxes[0]

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        checkbox
                    )

                    self.driver.execute_script(
                        "arguments[0].click();",
                        checkbox
                    )

                    time.sleep(2)

                    if checkbox.is_selected():
                        return " ".join(row.text.split())

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            "Student checkbox could not be selected."
        )

    def wait_for_promoted_successfully(self, timeout=30):
        success_xpath = (
            "//*[contains(translate(normalize-space(), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'promot')]"
        )

        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(
                (By.XPATH, success_xpath)
            )
        )

        return True