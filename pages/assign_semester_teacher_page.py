# # pages/assign_semester_teacher_page.py
#
# import time
#
# from selenium.common.exceptions import (
#     StaleElementReferenceException
# )
#
# from selenium.webdriver.common.by import By
#
# from selenium.webdriver.support.ui import (
#     WebDriverWait,
#     Select
# )
#
# from selenium.webdriver.support import (
#     expected_conditions as EC
# )
#
#
# class AssignSemesterTeacherPage:
#
#     EMAIL = (
#         By.XPATH,
#         "//input[@type='email' or @name='email']"
#     )
#
#     PASSWORD = (
#         By.XPATH,
#         "//input[@type='password' or @name='password']"
#     )
#
#     LOGIN_BUTTON = (
#         By.XPATH,
#         "//button[normalize-space()='Login']"
#     )
#
#     COURSE = (
#         By.XPATH,
#         "(//label[contains(normalize-space(),'Select Course')]/following::select[1])[1]"
#     )
#
#     SEMESTER = (
#         By.XPATH,
#         "(//label[contains(normalize-space(),'Select Semester')]/following::select[1])[1]"
#     )
#
#     TEACHER_SEARCH = (
#         By.XPATH,
#         "//input[contains(@placeholder,'Search teachers')]"
#     )
#
#     SAVE_BUTTON = (
#         By.XPATH,
#         "//button[@type='submit'] "
#         "| //button[contains(@class,'btn')]//*[name()='svg']/ancestor::button "
#         "| //button[contains(@class,'mat-fab')] "
#         "| //button[contains(@class,'floating')]"
#     )
#
#     YES_SAVE_BUTTON = (
#         By.XPATH,
#         "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes')]"
#     )
#
#     ASSIGNED_TABLE = (
#         By.XPATH,
#         "//table"
#     )
#
#     def __init__(self, driver, timeout=20):
#
#         self.driver = driver
#
#         self.wait = WebDriverWait(
#             driver,
#             timeout
#         )
#
#     def scroll(self, locator):
#
#         element = self.wait.until(
#             EC.presence_of_element_located(locator)
#         )
#
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({block:'center'});",
#             element
#         )
#
#         time.sleep(0.5)
#
#         return element
#
#     def click(self, locator):
#
#         element = self.scroll(locator)
#
#         try:
#
#             self.wait.until(
#                 EC.element_to_be_clickable(locator)
#             )
#
#             element.click()
#
#         except Exception:
#
#             self.driver.execute_script(
#                 "arguments[0].click();",
#                 element
#             )
#
#         time.sleep(1.5)
#
#     def enter_text(self, locator, text):
#
#         element = self.scroll(locator)
#
#         element.clear()
#
#         element.send_keys(text)
#
#         self.driver.execute_script(
#             """
#             arguments[0].dispatchEvent(
#                 new Event('input', { bubbles: true })
#             );
#
#             arguments[0].dispatchEvent(
#                 new Event('change', { bubbles: true })
#             );
#
#             arguments[0].dispatchEvent(
#                 new Event('blur', { bubbles: true })
#             );
#             """,
#             element
#         )
#
#         time.sleep(1)
#
#     def select_element_by_text(
#             self,
#             select_element,
#             visible_text
#     ):
#
#         Select(select_element).select_by_visible_text(
#             visible_text
#         )
#
#         self.driver.execute_script(
#             """
#             arguments[0].dispatchEvent(
#                 new Event('change', { bubbles: true })
#             );
#             """,
#             select_element
#         )
#
#         time.sleep(1.5)
#
#     def select_by_visible_text(
#             self,
#             locator,
#             visible_text
#     ):
#
#         element = self.scroll(locator)
#
#         self.select_element_by_text(
#             element,
#             visible_text
#         )
#
#     def select_first_valid_option(
#             self,
#             locator,
#             field_name,
#             timeout=25
#     ):
#
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#
#             try:
#
#                 element = self.scroll(locator)
#
#                 select = Select(element)
#
#                 valid_options = [
#
#                     option.text.strip()
#
#                     for option in select.options
#
#                     if option.text.strip()
#
#                     and option.text.strip().lower() not in [
#
#                         "select",
#                         "--select--",
#                         "-select-",
#                         f"select {field_name.lower()}"
#
#                     ]
#
#                 ]
#
#                 if len(valid_options) > 0:
#
#                     selected_text = valid_options[0]
#
#                     select.select_by_visible_text(
#                         selected_text
#                     )
#
#                     self.driver.execute_script(
#                         """
#                         arguments[0].dispatchEvent(
#                             new Event('change', { bubbles: true })
#                         );
#                         """,
#                         element
#                     )
#
#                     time.sleep(1.5)
#
#                     return selected_text
#
#             except StaleElementReferenceException:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError(
#             f"No valid {field_name} option found."
#         )
#
#     def select_course(self):
#
#         try:
#
#             self.select_by_visible_text(
#                 self.COURSE,
#                 "BBA (Hospital Management)"
#             )
#
#             return "BBA (Hospital Management)"
#
#         except Exception:
#
#             return self.select_first_valid_option(
#                 self.COURSE,
#                 "course"
#             )
#
#     def select_semester(self):
#
#         try:
#
#             self.select_by_visible_text(
#                 self.SEMESTER,
#                 "4th Sem"
#             )
#
#             return "4th Sem"
#
#         except Exception:
#
#             return self.select_first_valid_option(
#                 self.SEMESTER,
#                 "semester"
#             )
#
#     def search_teacher(self, teacher_name):
#
#         self.enter_text(
#             self.TEACHER_SEARCH,
#             teacher_name
#         )
#
#     def select_teacher_chip(
#             self,
#             teacher_name
#     ):
#
#         end_time = time.time() + 20
#
#         while time.time() < end_time:
#
#             try:
#
#                 teacher_chip = self.driver.find_element(
#                     By.XPATH,
#                     f"//*[contains(normalize-space(),'{teacher_name}')]"
#                 )
#
#                 self.driver.execute_script(
#                     "arguments[0].scrollIntoView({block:'center'});",
#                     teacher_chip
#                 )
#
#                 time.sleep(1)
#
#                 try:
#                     teacher_chip.click()
#
#                 except Exception:
#
#                     self.driver.execute_script(
#                         "arguments[0].click();",
#                         teacher_chip
#                     )
#
#                 time.sleep(2)
#
#                 return teacher_name
#
#             except Exception:
#
#                 time.sleep(1)
#
#         raise AssertionError(
#             f"Teacher chip not found: {teacher_name}"
#         )
#
#     def click_save(self):
#
#         end_time = time.time() + 20
#
#         while time.time() < end_time:
#
#             try:
#
#                 buttons = self.driver.find_elements(
#                     By.XPATH,
#                     "//button[@type='submit'] "
#                     "| //button[contains(@class,'btn')]//*[name()='svg']/ancestor::button "
#                     "| //button[contains(@class,'mat-fab')] "
#                     "| //button[contains(@class,'floating')]"
#                 )
#
#                 visible_buttons = []
#
#                 for button in buttons:
#
#                     try:
#
#                         if button.is_displayed():
#
#                             visible_buttons.append(
#                                 button
#                             )
#
#                     except StaleElementReferenceException:
#                         continue
#
#                 if len(visible_buttons) > 0:
#
#                     save_button = visible_buttons[0]
#
#                     self.driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});",
#                         save_button
#                     )
#
#                     time.sleep(1)
#
#                     try:
#                         save_button.click()
#
#                     except Exception:
#
#                         self.driver.execute_script(
#                             "arguments[0].click();",
#                             save_button
#                         )
#
#                     time.sleep(2)
#
#                     return True
#
#             except Exception:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError(
#             "Save button was not found."
#         )
#
#     def confirm_save(self):
#
#         end_time = time.time() + 20
#
#         while time.time() < end_time:
#
#             try:
#
#                 yes_buttons = self.driver.find_elements(
#                     By.XPATH,
#                     "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes')]"
#                 )
#
#                 visible_buttons = []
#
#                 for button in yes_buttons:
#
#                     try:
#
#                         if button.is_displayed():
#
#                             visible_buttons.append(
#                                 button
#                             )
#
#                     except StaleElementReferenceException:
#                         continue
#
#                 if len(visible_buttons) > 0:
#
#                     yes_button = visible_buttons[0]
#
#                     try:
#                         yes_button.click()
#
#                     except Exception:
#
#                         self.driver.execute_script(
#                             "arguments[0].click();",
#                             yes_button
#                         )
#
#                     time.sleep(2)
#
#                     return True
#
#             except Exception:
#                 pass
#
#             time.sleep(1)
#
#         return True
#
#     def wait_for_assigned_teacher_result(
#             self,
#             teacher_names,
#             timeout=40
#     ):
#
#         teacher_names = [
#             teacher.lower().strip()
#             for teacher in teacher_names
#         ]
#
#         end_time = time.time() + timeout
#
#         while time.time() < end_time:
#
#             try:
#
#                 body_text = " ".join(
#                     self.driver.find_element(
#                         By.TAG_NAME,
#                         "body"
#                     ).text.lower().split()
#                 )
#
#                 all_found = all(
#                     teacher in body_text
#                     for teacher in teacher_names
#                 )
#
#                 if all_found:
#                     return True
#
#             except StaleElementReferenceException:
#                 pass
#
#             time.sleep(1)
#
#         raise AssertionError(
#             f"Assigned teachers not found: {teacher_names}"
#         )


import time

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import (
    WebDriverWait,
    Select
)

from selenium.webdriver.support import (
    expected_conditions as EC
)


class AssignSemesterTeacherPage:

    EMAIL = (
        By.XPATH,
        "//input[@type='email' or @name='email']"
    )

    PASSWORD = (
        By.XPATH,
        "//input[@type='password' or @name='password']"
    )

    LOGIN_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Login']"
    )

    COURSE = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Select Course')]/following::select[1])[1]"
    )

    SEMESTER = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Select Semester')]/following::select[1])[1]"
    )

    TEACHER_SEARCH = (
        By.XPATH,
        "//input[contains(@placeholder,'Search teachers')]"
    )

    SAVE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    YES_SAVE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes')]"
    )

    ASSIGNED_TABLE = (
        By.XPATH,
        "//table"
    )

    PAGINATION_NEXT = (
        By.XPATH,
        "//li[@class='pagination-next ng-star-inserted']//a[@class='ng-star-inserted']"
    )

    EDIT_BUTTON = (
        By.XPATH,
        "(//table//button[contains(@class,'edit') "
        "or .//*[contains(@class,'edit')]])[last()]"
    )

    DELETE_BUTTON = (
        By.XPATH,
        "(//table//button[contains(@class,'delete') "
        "or .//*[contains(@class,'trash')]])[last()]"
    )

    CONFIRM_DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes')]"
    )

    def __init__(self, driver, timeout=20):

        self.driver = driver

        self.wait = WebDriverWait(
            driver,
            timeout
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

        time.sleep(1.5)

    def enter_text(self, locator, text):

        element = self.scroll(locator)

        element.clear()

        element.send_keys(text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(
                new Event('input', { bubbles: true })
            );

            arguments[0].dispatchEvent(
                new Event('change', { bubbles: true })
            );

            arguments[0].dispatchEvent(
                new Event('blur', { bubbles: true })
            );
            """,
            element
        )

        time.sleep(1)

    def select_element_by_text(
            self,
            select_element,
            visible_text
    ):

        Select(select_element).select_by_visible_text(
            visible_text
        )

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(
                new Event('change', { bubbles: true })
            );
            """,
            select_element
        )

        time.sleep(1.5)

    def select_by_visible_text(
            self,
            locator,
            visible_text
    ):

        element = self.scroll(locator)

        self.select_element_by_text(
            element,
            visible_text
        )

    def select_first_valid_option(
            self,
            locator,
            field_name,
            timeout=25
    ):

        end_time = time.time() + timeout

        while time.time() < end_time:

            try:

                element = self.scroll(locator)

                select = Select(element)

                valid_options = [

                    option.text.strip()

                    for option in select.options

                    if option.text.strip()

                    and option.text.strip().lower() not in [

                        "select",
                        "--select--",
                        "-select-",
                        f"select {field_name.lower()}"

                    ]

                ]

                if len(valid_options) > 0:

                    selected_text = valid_options[0]

                    select.select_by_visible_text(
                        selected_text
                    )

                    self.driver.execute_script(
                        """
                        arguments[0].dispatchEvent(
                            new Event('change', { bubbles: true })
                        );
                        """,
                        element
                    )

                    time.sleep(1.5)

                    return selected_text

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found."
        )

    def select_course(self):

        try:

            self.select_by_visible_text(
                self.COURSE,
                "BBA (Hospital Management)"
            )

            return "BBA (Hospital Management)"

        except Exception:

            return self.select_first_valid_option(
                self.COURSE,
                "course"
            )

    def select_semester(self):

        try:

            self.select_by_visible_text(
                self.SEMESTER,
                "4th Sem"
            )

            return "4th Sem"

        except Exception:

            return self.select_first_valid_option(
                self.SEMESTER,
                "semester"
            )

    def search_teacher(self, teacher_name):

        self.enter_text(
            self.TEACHER_SEARCH,
            teacher_name
        )

    def select_teacher_chip(
            self,
            teacher_name
    ):

        end_time = time.time() + 20

        while time.time() < end_time:

            try:

                teacher_chip = self.driver.find_element(
                    By.XPATH,
                    f"//*[contains(normalize-space(),'{teacher_name}')]"
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    teacher_chip
                )

                time.sleep(1)

                try:
                    teacher_chip.click()

                except Exception:

                    self.driver.execute_script(
                        "arguments[0].click();",
                        teacher_chip
                    )

                time.sleep(2)

                return teacher_name

            except Exception:

                time.sleep(1)

        raise AssertionError(
            f"Teacher chip not found: {teacher_name}"
        )

    def click_save(self):

        end_time = time.time() + 20

        while time.time() < end_time:

            try:

                buttons = self.driver.find_elements(
                    *self.SAVE_BUTTON
                )

                visible_buttons = []

                for button in buttons:

                    try:

                        if button.is_displayed():

                            visible_buttons.append(
                                button
                            )

                    except StaleElementReferenceException:
                        continue

                if len(visible_buttons) > 0:

                    save_button = visible_buttons[0]

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        save_button
                    )

                    time.sleep(1)

                    try:
                        save_button.click()

                    except Exception:

                        self.driver.execute_script(
                            "arguments[0].click();",
                            save_button
                        )

                    time.sleep(2)

                    return True

            except Exception:
                pass

            time.sleep(1)

        raise AssertionError(
            "Save button was not found."
        )

    def confirm_save(self):

        end_time = time.time() + 20

        while time.time() < end_time:

            try:

                yes_buttons = self.driver.find_elements(
                    *self.YES_SAVE_BUTTON
                )

                visible_buttons = []

                for button in yes_buttons:

                    try:

                        if button.is_displayed():

                            visible_buttons.append(
                                button
                            )

                    except StaleElementReferenceException:
                        continue

                if len(visible_buttons) > 0:

                    yes_button = visible_buttons[0]

                    try:
                        yes_button.click()

                    except Exception:

                        self.driver.execute_script(
                            "arguments[0].click();",
                            yes_button
                        )

                    time.sleep(2)

                    return True

            except Exception:
                pass

            time.sleep(1)

        return True

    def wait_for_assigned_teacher_result(
            self,
            teacher_names,
            timeout=40
    ):

        teacher_names = [
            teacher.lower().strip()
            for teacher in teacher_names
        ]

        end_time = time.time() + timeout

        while time.time() < end_time:

            try:

                body_text = " ".join(
                    self.driver.find_element(
                        By.TAG_NAME,
                        "body"
                    ).text.lower().split()
                )

                all_found = all(
                    teacher in body_text
                    for teacher in teacher_names
                )

                if all_found:
                    return True

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"Assigned teachers not found: {teacher_names}"
        )

    # ---------------------------------------------------------
    # NEW CRUD METHODS
    # ---------------------------------------------------------

    def scroll_to_bottom(self):

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(2)

    def click_next_pagination(self):

        end_time = time.time() + 20

        while time.time() < end_time:

            try:

                next_button = self.wait.until(
                    EC.element_to_be_clickable(
                        self.PAGINATION_NEXT
                    )
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    next_button
                )

                time.sleep(1)

                try:
                    next_button.click()

                except Exception:

                    self.driver.execute_script(
                        "arguments[0].click();",
                        next_button
                    )

                time.sleep(3)

                return True

            except Exception:

                time.sleep(1)

        raise AssertionError(
            "Pagination next button not found."
        )

    def verify_recent_teacher_record(
            self,
            teacher_name
    ):

        teacher_locator = (
            By.XPATH,
            f"//table//*[contains(normalize-space(),'{teacher_name}')]"
        )

        self.wait.until(
            EC.visibility_of_element_located(
                teacher_locator
            )
        )

        return True

    def click_edit_button(self):

        self.click(
            self.EDIT_BUTTON
        )

    def update_teacher(
            self,
            old_teacher,
            new_teacher
    ):

        try:

            remove_icon = (
                By.XPATH,
                f"//*[contains(normalize-space(),'{old_teacher}')]"
                f"/following::*[name()='svg'][1]"
            )

            self.click(remove_icon)

            time.sleep(1)

        except Exception:
            pass

        self.search_teacher(
            new_teacher
        )

        self.select_teacher_chip(
            new_teacher
        )

    def click_delete_button(self):

        self.click(
            self.DELETE_BUTTON
        )

    def confirm_delete(self):

        try:

            self.click(
                self.CONFIRM_DELETE_BUTTON
            )

        except TimeoutException:
            pass

    def verify_teacher_deleted(
            self,
            teacher_name
    ):

        elements = self.driver.find_elements(
            By.XPATH,
            f"//table//*[contains(normalize-space(),'{teacher_name}')]"
        )

        assert len(elements) == 0, (
            f"Teacher still exists: {teacher_name}"
        )