# import time
#
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
#
#
# class StudentGroupPage:
#     EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
#     PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
#     LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")
#
#     COURSE = (
#         By.XPATH,
#         "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
#     )
#
#     SEMESTER = (
#         By.XPATH,
#         "//label[contains(normalize-space(),'Select Semester')]/following::select[1]"
#     )
#
#     GROUP = (
#         By.XPATH,
#         "//label[contains(normalize-space(),'Select Group')]/following::select[1]"
#     )
#
#     CHECK_ALL_BUTTON = (
#         By.XPATH,
#         "//button[contains(normalize-space(),'Check All')]"
#     )
#
#     FIRST_STUDENT_CHECKBOX = (
#         By.XPATH,
#         "(//input[@type='checkbox'])[1]"
#     )
#
#     STUDENT_CHECKBOXES = (
#         By.XPATH,
#         "//input[@type='checkbox']"
#     )
#
#     SUBMIT_BUTTON = (
#         By.XPATH,
#         "//button[normalize-space()='Submit']"
#     )
#
#     UPDATE_BUTTON = (
#         By.XPATH,
#         "//button[normalize-space()='Update']"
#     )
#
#     CANCEL_BUTTON = (
#         By.XPATH,
#         "//button[normalize-space()='Cancel']"
#     )
#
#     SEARCH_OR_FILTER = (
#         By.XPATH,
#         "//input[contains(@placeholder,'Search') or contains(@placeholder,'Filter')]"
#     )
#
#     YES_DELETE_BUTTON = (
#         By.XPATH,
#         "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
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
#                     "select course",
#                     "select semester",
#                     "select group"
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
#     def select_last_valid_option(self, locator, field_name, timeout=25):
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
#                     "select course",
#                     "select semester",
#                     "select group"
#                 ]
#             ]
#
#             if len(valid_options) > 0:
#                 selected_text = valid_options[-1].text.strip()
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
#     def wait_for_semester_options(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             element = self.scroll(self.SEMESTER)
#             select = Select(element)
#
#             valid_options = [
#                 option.text.strip()
#                 for option in select.options
#                 if option.text.strip()
#                 and option.text.strip().lower() not in [
#                     "select",
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
#             "Semester dropdown options did not load after selecting course."
#         )
#
#     def wait_for_group_options(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             element = self.scroll(self.GROUP)
#             select = Select(element)
#
#             valid_options = [
#                 option.text.strip()
#                 for option in select.options
#                 if option.text.strip()
#                 and option.text.strip().lower() not in [
#                     "select",
#                     "select group"
#                 ]
#             ]
#
#             if len(valid_options) > 0:
#                 return True
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "Group dropdown options did not load after selecting course and semester."
#         )
#
#     def wait_for_student_checkboxes(self, timeout=25):
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#             checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
#
#             if len(checkboxes) > 0:
#                 return True
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "Student checkbox list did not load after selecting course, semester and group."
#         )
#
#     def get_first_student_name(self):
#         self.wait_for_student_checkboxes(timeout=25)
#
#         first_checkbox = self.driver.find_element(By.XPATH, "(//input[@type='checkbox'])[3]")
#
#         parent_text = self.driver.execute_script(
#             """
#             let el = arguments[0];
#
#             while (el && el.innerText.trim() === '') {
#                 el = el.parentElement;
#             }
#
#             return el ? el.innerText : '';
#             """,
#             first_checkbox
#         )
#
#         student_name = " ".join(parent_text.split())
#
#         if student_name:
#             student_name = student_name.split(" ", 1)[-1]
#             student_name = student_name.split("-(")[0].strip()
#
#         assert student_name != "", "First student name could not be detected."
#
#         return student_name
#
#     def click_first_student_checkbox(self):
#         self.wait_for_student_checkboxes(timeout=25)
#
#         checkbox = self.driver.find_element(By.XPATH, "(//input[@type='checkbox'])[3]")
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             checkbox
#         )
#
#         if not checkbox.is_selected():
#             try:
#                 checkbox.click()
#             except Exception:
#                 self.driver.execute_script("arguments[0].click();", checkbox)
#
#         time.sleep(1)
#
#     def click_check_all(self):
#         self.click(self.CHECK_ALL_BUTTON)
#
#     def scroll_table_to_right(self):
#         self.driver.execute_script(
#             """
#             const elements = document.querySelectorAll('*');
#
#             for (const el of elements) {
#                 if (el.scrollWidth > el.clientWidth) {
#                     el.scrollLeft = el.scrollWidth;
#                 }
#             }
#             """
#         )
#
#         time.sleep(1)
#
#     def get_exact_row_by_values(self, expected_values):
#         expected_values = [
#             str(value).lower().strip()
#             for value in expected_values
#         ]
#
#         rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")
#
#         for row in rows:
#             row_text = " ".join(row.text.lower().split())
#
#             if all(value in row_text for value in expected_values):
#                 return row
#
#         table_text = ""
#
#         try:
#             table_text = self.driver.find_element(By.XPATH, "//table//tbody").text
#         except Exception:
#             table_text = ""
#
#         raise AssertionError(
#             f"Exact student group row not found. "
#             f"Expected values: {expected_values}. "
#             f"Actual table text: {table_text}"
#         )
#
#     def click_edit_for_exact_row(self, expected_values):
#         self.scroll_table_to_right()
#
#         row = self.get_exact_row_by_values(expected_values)
#
#         edit_button = row.find_element(
#             By.XPATH,
#             "(.//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
#         )
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             edit_button
#         )
#
#         try:
#             edit_button.click()
#         except Exception:
#             self.driver.execute_script("arguments[0].click();", edit_button)
#
#         time.sleep(1.2)
#
#     def click_delete_for_exact_row(self, expected_values):
#         self.scroll_table_to_right()
#
#         row = self.get_exact_row_by_values(expected_values)
#
#         delete_button = row.find_element(
#             By.XPATH,
#             "(.//*[local-name()='svg' or self::i or self::button or self::mat-icon])[last()]"
#         )
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             delete_button
#         )
#
#         try:
#             delete_button.click()
#         except Exception:
#             self.driver.execute_script("arguments[0].click();", delete_button)
#
#         time.sleep(1.2)
#
#     def login(self, email, password):
#         self.enter_text(self.EMAIL, email)
#         self.enter_text(self.PASSWORD, password)
#         self.click(self.LOGIN_BUTTON)
#
#     def select_course(self):
#         self.select_by_visible_text(self.COURSE, "B.SC. COMPUTER SCIENCE")
#         time.sleep(2)
#         return "B.SC. COMPUTER SCIENCE"
#
#     def select_semester(self):
#         self.wait_for_semester_options(timeout=25)
#         self.select_by_visible_text(self.SEMESTER, "2nd Sem")
#         time.sleep(2)
#         return "2nd Sem"
#
#     def select_group(self):
#         self.wait_for_group_options(timeout=25)
#         selected_group = self.select_first_valid_option(
#             self.GROUP,
#             "group",
#             timeout=25
#         )
#         time.sleep(2)
#         return selected_group
#
#     def select_edit_group(self):
#         self.wait_for_group_options(timeout=25)
#         selected_group = self.select_last_valid_option(
#             self.GROUP,
#             "group",
#             timeout=25
#         )
#         time.sleep(2)
#         return selected_group
#
#     def enter_search_or_filter(self, value):
#         self.enter_text(self.SEARCH_OR_FILTER, value)
#
#     def click_submit(self):
#         self.click(self.SUBMIT_BUTTON)
#
#     def click_update(self):
#         self.click(self.UPDATE_BUTTON)
#
#     def click_cancel(self):
#         self.click(self.CANCEL_BUTTON)
#
#     def confirm_delete(self):
#         self.click(self.YES_DELETE_BUTTON)


import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class StudentGroupPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Semester')]/following::select[1]"
    )

    GROUP = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Group')]/following::select[1]"
    )

    CHECK_ALL_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Check All')]"
    )

    FIRST_STUDENT_CHECKBOX = (
        By.XPATH,
        "(//input[@type='checkbox'])[1]"
    )

    STUDENT_CHECKBOXES = (
        By.XPATH,
        "//input[@type='checkbox']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
    )

    CANCEL_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Cancel']"
    )

    SEARCH_OR_FILTER = (
        By.XPATH,
        "//input[contains(@placeholder,'Search') or contains(@placeholder,'Filter')]"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
    )

    NEXT_PAGE_BUTTON = (
        By.XPATH,
        "//li[contains(@class,'pagination-next')]//a"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

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
        element = self.scroll(locator)

        try:
            self.wait.until(
                EC.element_to_be_clickable(locator)
            )
            element.click()

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

        time.sleep(1.2)

    def enter_text(self, locator, text):
        element = self.scroll(locator)

        element.clear()
        element.send_keys(text)

        time.sleep(0.7)

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        try:
            Select(element).select_by_visible_text(
                visible_text
            )

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

        time.sleep(1.5)

    def select_first_valid_option(
            self,
            locator,
            field_name,
            timeout=25
    ):
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
                    "select course",
                    "select semester",
                    "select group"
                ]
            ]

            if len(valid_options) > 0:

                selected_text = valid_options[0].text.strip()

                select.select_by_visible_text(
                    selected_text
                )

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                    """,
                    element
                )

                time.sleep(1.5)

                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found."
        )

    def select_last_valid_option(
            self,
            locator,
            field_name,
            timeout=25
    ):
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
                    "select course",
                    "select semester",
                    "select group"
                ]
            ]

            if len(valid_options) > 0:

                selected_text = valid_options[-1].text.strip()

                select.select_by_visible_text(
                    selected_text
                )

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                    """,
                    element
                )

                time.sleep(1.5)

                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found."
        )

    def wait_for_semester_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:

            element = self.scroll(self.SEMESTER)

            select = Select(element)

            valid_options = [
                option.text.strip()
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "Semester dropdown options did not load."
        )

    def wait_for_group_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:

            element = self.scroll(self.GROUP)

            select = Select(element)

            valid_options = [
                option.text.strip()
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "select group"
                ]
            ]

            if len(valid_options) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "Group dropdown options did not load."
        )

    def wait_for_student_checkboxes(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:

            checkboxes = self.driver.find_elements(
                By.XPATH,
                "//input[@type='checkbox']"
            )

            if len(checkboxes) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "Student checkbox list did not load."
        )

    def get_first_student_name(self):
        self.wait_for_student_checkboxes()

        first_checkbox = self.driver.find_element(
            By.XPATH,
            "(//input[@type='checkbox'])[1]"
        )

        parent_text = self.driver.execute_script(
            """
            let el = arguments[0];

            while (el && el.innerText.trim() === '') {
                el = el.parentElement;
            }

            return el ? el.innerText : '';
            """,
            first_checkbox
        )

        student_name = " ".join(parent_text.split())

        if student_name:
            student_name = student_name.split(" ", 1)[-1]
            student_name = student_name.split("-(")[0].strip()

        assert student_name != ""

        return student_name

    def click_first_student_checkbox(self):
        self.wait_for_student_checkboxes()

        checkbox = self.driver.find_element(
            By.XPATH,
            "(//input[@type='checkbox'])[1]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            checkbox
        )

        if not checkbox.is_selected():

            try:
                checkbox.click()

            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    checkbox
                )

        time.sleep(1)

    # def uncheck_selected_student_if_checked(self):
    #     checkboxes = self.driver.find_elements(
    #         By.XPATH,
    #         "//input[@type='checkbox']"
    #     )
    #
    #     for checkbox in checkboxes:
    #
    #         try:
    #             if checkbox.is_selected():
    #
    #                 self.driver.execute_script(
    #                     "arguments[0].scrollIntoView({block:'center'});",
    #                     checkbox
    #                 )
    #
    #                 try:
    #                     checkbox.click()
    #
    #                 except Exception:
    #                     self.driver.execute_script(
    #                         "arguments[0].click();",
    #                         checkbox
    #                     )
    #
    #                 time.sleep(1)
    #                 return
    #
    #         except Exception:
    #             continue
    #
    # def get_first_unchecked_student_name(self):
    #     self.wait_for_student_checkboxes(timeout=25)
    #
    #     checkboxes = self.driver.find_elements(
    #         By.XPATH,
    #         "//input[@type='checkbox']"
    #     )
    #
    #     unchecked_students = []
    #
    #     for index, checkbox in enumerate(checkboxes):
    #
    #         try:
    #             parent_text = self.driver.execute_script(
    #                 """
    #                 let el = arguments[0];
    #
    #                 while (el && el.innerText.trim() === '') {
    #                     el = el.parentElement;
    #                 }
    #
    #                 return el ? el.innerText : '';
    #                 """,
    #                 checkbox
    #             )
    #
    #             student_name = " ".join(parent_text.split())
    #
    #             if student_name:
    #                 student_name = student_name.split(" ", 1)[-1]
    #                 student_name = student_name.split("-(")[0].strip()
    #
    #             unchecked_students.append({
    #                 "checkbox": checkbox,
    #                 "name": student_name,
    #                 "selected": checkbox.is_selected(),
    #                 "index": index
    #             })
    #
    #         except Exception:
    #             continue
    #
    #     # SKIP FIRST UNCHECKED (OLD STUDENT)
    #     unchecked_count = 0
    #
    #     for student in unchecked_students:
    #
    #         if not student["selected"]:
    #
    #             unchecked_count += 1
    #
    #             if unchecked_count == 1:
    #                 continue
    #
    #             return student["name"]
    #
    #     raise AssertionError(
    #         "No another unchecked student found during edit."
    #     )
    #
    # def click_first_unchecked_student_checkbox(self):
    #     self.wait_for_student_checkboxes(timeout=25)
    #
    #     checkboxes = self.driver.find_elements(
    #         By.XPATH,
    #         "//input[@type='checkbox']"
    #     )
    #
    #     unchecked_students = []
    #
    #     for checkbox in checkboxes:
    #
    #         try:
    #             unchecked_students.append({
    #                 "checkbox": checkbox,
    #                 "selected": checkbox.is_selected()
    #             })
    #
    #         except Exception:
    #             continue
    #
    #     # SKIP FIRST UNCHECKED (OLD STUDENT)
    #     unchecked_count = 0
    #
    #     for student in unchecked_students:
    #
    #         if not student["selected"]:
    #
    #             unchecked_count += 1
    #
    #             if unchecked_count == 1:
    #                 continue
    #
    #             checkbox = student["checkbox"]
    #
    #             self.driver.execute_script(
    #                 "arguments[0].scrollIntoView({block:'center'});",
    #                 checkbox
    #             )
    #
    #             try:
    #                 checkbox.click()
    #             except Exception:
    #                 self.driver.execute_script(
    #                     "arguments[0].click();",
    #                     checkbox
    #                 )
    #
    #             time.sleep(1)
    #             return
    #
    #     raise AssertionError(
    #         "No another unchecked student checkbox found during edit."
    #     )
    def get_student_checkboxes_with_names(self):
        """
        Returns all visible student checkboxes with names.
        Works for div/table layouts both.
        """

        student_data = []

        checkbox_elements = self.driver.find_elements(
            By.XPATH,
            "//input[@type='checkbox']"
        )

        for checkbox in checkbox_elements:

            try:
                if not checkbox.is_displayed():
                    continue

                parent_text = self.driver.execute_script(
                    """
                    let el = arguments[0];

                    while (
                        el &&
                        (
                            el.innerText === undefined ||
                            el.innerText.trim() === ''
                        )
                    ) {
                        el = el.parentElement;
                    }

                    return el ? el.innerText : '';
                    """,
                    checkbox
                )

                student_name = " ".join(parent_text.split())

                if not student_name:
                    continue

                # CLEAN NAME
                student_name = student_name.split("-(")[0].strip()

                student_data.append({
                    "checkbox": checkbox,
                    "name": student_name,
                    "selected": checkbox.is_selected()
                })

            except Exception:
                continue

        return student_data

    def get_selected_student_name(self):

        students = self.get_student_checkboxes_with_names()

        for student in students:

            if student["selected"]:
                return student["name"]

        raise AssertionError(
            "No selected student found."
        )

    def uncheck_selected_student_if_checked(self):

        students = self.get_student_checkboxes_with_names()

        for student in students:

            if student["selected"]:

                checkbox = student["checkbox"]

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    checkbox
                )

                self.driver.execute_script(
                    "arguments[0].click();",
                    checkbox
                )

                time.sleep(2)

                # VERIFY UNCHECKED
                if checkbox.is_selected():
                    self.driver.execute_script(
                        "arguments[0].click();",
                        checkbox
                    )

                    time.sleep(2)

                return student["name"]

        raise AssertionError(
            "No selected student checkbox found."
        )

    def click_first_unchecked_student_checkbox(
            self,
            old_student_name
    ):

        students = self.get_student_checkboxes_with_names()

        for student in students:

            student_name = student["name"]
            checkbox = student["checkbox"]

            # DO NOT SELECT OLD STUDENT AGAIN
            if (
                    student_name.lower().strip()
                    != old_student_name.lower().strip()
            ):

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    checkbox
                )

                self.driver.execute_script(
                    "arguments[0].click();",
                    checkbox
                )

                time.sleep(2)

                # FORCE ANGULAR CHANGE DETECTION
                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(
                        new Event('change', { bubbles:true })
                    );

                    arguments[0].dispatchEvent(
                        new Event('input', { bubbles:true })
                    );
                    """,
                    checkbox
                )

                time.sleep(2)

                if checkbox.is_selected():
                    return student_name

        raise AssertionError(
            "No different student checkbox found."
        )

    def scroll_table_to_right(self):
        self.driver.execute_script(
            """
            const elements = document.querySelectorAll('*');

            for (const el of elements) {
                if (el.scrollWidth > el.clientWidth) {
                    el.scrollLeft = el.scrollWidth;
                }
            }
            """
        )

        time.sleep(1)

    def get_exact_row_by_values(self, expected_values):
        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        max_pages = 50
        current_page = 1

        while current_page <= max_pages:

            rows = self.driver.find_elements(
                By.XPATH,
                "//table//tbody//tr"
            )

            for row in rows:

                row_text = " ".join(
                    row.text.lower().split()
                )

                if all(
                        value in row_text
                        for value in expected_values
                ):
                    return row

            try:
                next_btn = self.driver.find_element(
                    *self.NEXT_PAGE_BUTTON
                )

                parent_class = next_btn.find_element(
                    By.XPATH,
                    "./parent::*"
                ).get_attribute("class").lower()

                if "disabled" in parent_class:
                    break

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    next_btn
                )

                try:
                    next_btn.click()

                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        next_btn
                    )

                time.sleep(2)

                current_page += 1

            except Exception:
                break

        raise AssertionError(
            f"Exact row not found: {expected_values}"
        )

    def click_edit_for_exact_row(self, expected_values):
        self.scroll_table_to_right()

        row = self.get_exact_row_by_values(
            expected_values
        )

        edit_button = row.find_element(
            By.XPATH,
            "(.//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            edit_button
        )

        try:
            edit_button.click()

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                edit_button
            )

        time.sleep(1.2)

    def click_delete_for_exact_row(self, expected_values):
        self.scroll_table_to_right()

        row = self.get_exact_row_by_values(
            expected_values
        )

        delete_button = row.find_element(
            By.XPATH,
            "(.//*[local-name()='svg' or self::i or self::button or self::mat-icon])[last()]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            delete_button
        )

        try:
            delete_button.click()

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                delete_button
            )

        time.sleep(1.2)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_course(self):
        self.select_by_visible_text(
            self.COURSE,
            "Bachelor of Business Administration"
        )

        time.sleep(2)

        return "Bachelor of Business Administration"

    def select_semester(self):
        self.wait_for_semester_options()

        self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem"
        )

        time.sleep(2)

        return "2nd Sem"

    def select_group(self):
        self.wait_for_group_options()

        selected_group = self.select_first_valid_option(
            self.GROUP,
            "group"
        )

        time.sleep(2)

        return selected_group

    def select_edit_group(self):
        self.wait_for_group_options()

        selected_group = self.select_last_valid_option(
            self.GROUP,
            "group"
        )

        time.sleep(2)

        return selected_group

    def enter_search_or_filter(self, value):
        self.enter_text(
            self.SEARCH_OR_FILTER,
            value
        )

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)
