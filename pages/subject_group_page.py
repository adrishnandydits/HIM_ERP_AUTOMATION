import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SubjectGroupPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    SUBJECT_GROUP_NAME = (
        By.XPATH,
        "//input[@placeholder='Enter subject group Name']"
    )

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Course')]/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Semester')]/following::select[1]"
    )

    SEARCH_SUBJECT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Search Subject')]/following::input[@placeholder='Search Or Filter'][1]"
    )

    SUBJECT_CHECKBOXES = (
        By.XPATH,
        "//label[contains(normalize-space(),'Subject List')]/following::input[@type='checkbox']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
    )

    TABLE_SEARCH = (
        By.XPATH,
        "(//input[@placeholder='Search Or Filter'])[last()]"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Yes') or contains(normalize-space(),'delete') or contains(normalize-space(),'OK') or contains(normalize-space(),'Ok')]"
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
            self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

        time.sleep(1.2)

    def enter_text(self, locator, value):
        element = self.scroll(locator)

        try:
            element.clear()
        except Exception:
            self.driver.execute_script("arguments[0].value='';", element)

        element.send_keys(str(value))

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('keyup', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(0.7)

    def select_first_valid_option(self, locator, field_name):
        invalid_options = [
            "select",
            "--select--",
            "-select-",
            "select course",
            "select semester"
        ]

        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                element = self.scroll(locator)
                select = Select(element)

                valid_options = [
                    option.text.strip()
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in invalid_options
                ]

                if len(valid_options) > 0:
                    selected_text = valid_options[0]
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

                    selected_value = Select(element).first_selected_option.text.strip()

                    if selected_value and selected_value.lower() not in invalid_options:
                        return selected_value

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found or selected after waiting 30 seconds."
        )

    def get_valid_select_options(self, locator):
        invalid_options = [
            "select",
            "--select--",
            "-select-",
            "select course",
            "select semester"
        ]

        element = self.scroll(locator)
        select = Select(element)

        return [
            option.text.strip()
            for option in select.options
            if option.text.strip()
            and option.text.strip().lower() not in invalid_options
        ]

    def select_option(self, locator, visible_text, field_name):
        element = self.scroll(locator)
        Select(element).select_by_visible_text(visible_text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(2)

        selected_value = Select(element).first_selected_option.text.strip()

        assert selected_value == visible_text, (
            f"{field_name} was not selected correctly. "
            f"Expected: {visible_text}, Actual: {selected_value}"
        )

        return selected_value

    def get_table_text(self):
        try:
            return self.driver.find_element(
                By.XPATH,
                "//table//tbody"
            ).text
        except Exception:
            return ""

    def table_has_course_semester_pair(self, course, semester):
        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        course_key = " ".join(course.lower().split())
        semester_key = " ".join(semester.lower().split())

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if course_key in row_text and semester_key in row_text:
                return True

        return False

    def select_available_course_and_semester(self):
        courses = self.get_valid_select_options(self.COURSE)

        for course in courses:
            try:
                selected_course = self.select_option(
                    self.COURSE,
                    course,
                    "course"
                )

                semesters = self.get_valid_select_options(self.SEMESTER)

                for semester in semesters:
                    if self.table_has_course_semester_pair(
                        selected_course,
                        semester
                    ):
                        continue

                    selected_semester = self.select_option(
                        self.SEMESTER,
                        semester,
                        "semester"
                    )

                    return selected_course, selected_semester

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                continue

        selected_course = self.select_first_valid_option(self.COURSE, "course")
        selected_semester = self.select_first_valid_option(self.SEMESTER, "semester")

        return selected_course, selected_semester

    def get_checkbox_text(self, checkbox):
        subject_text = ""

        text_xpaths = [
            "following::label[1]",
            "./ancestor::*[self::label or self::div][1]",
            "following::*[normalize-space()][1]"
        ]

        for xpath in text_xpaths:
            try:
                subject_text = checkbox.find_element(
                    By.XPATH,
                    xpath
                ).text.strip()

                if subject_text:
                    return subject_text
            except Exception:
                continue

        return subject_text

    def select_first_available_subject_checkbox(self):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                checkboxes = self.driver.find_elements(
                    *self.SUBJECT_CHECKBOXES
                )

                table_text = ""

                try:
                    table_text = self.driver.find_element(
                        By.XPATH,
                        "//table//tbody"
                    ).text.lower()
                except Exception:
                    table_text = ""

                for checkbox in checkboxes:
                    subject_text = self.get_checkbox_text(checkbox)

                    if not subject_text:
                        continue

                    subject_key = subject_text.lower().strip()

                    if subject_key in table_text:
                        continue

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
                    return subject_text

                first_checkbox = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "(//label[contains(normalize-space(),'Subject List')]/following::input[@type='checkbox'])[1]"
                        )
                    )
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    first_checkbox
                )

                subject_text = self.get_checkbox_text(first_checkbox)

                if not first_checkbox.is_selected():
                    try:
                        first_checkbox.click()
                    except Exception:
                        self.driver.execute_script(
                            "arguments[0].click();",
                            first_checkbox
                        )

                time.sleep(1)
                return subject_text

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

        raise AssertionError(
            "No subject checkbox found or selected after waiting 30 seconds."
        )

    def select_subject_checkbox_by_text(self, subject_text):
        checkbox = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//input[@type='checkbox'][following::label[contains(normalize-space(),\"{subject_text}\")][1]]"
                )
            )
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
        return subject_text

    def clear_selected_subjects(self):
        checkboxes = self.driver.find_elements(*self.SUBJECT_CHECKBOXES)

        for checkbox in checkboxes:
            try:
                if checkbox.is_selected():
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        checkbox
                    )
                    checkbox.click()
                    time.sleep(0.3)
            except Exception:
                continue

    def click_edit_for_exact_row(self, expected_values):
        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        matching_row = None

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in expected_values):
                matching_row = row

        if matching_row:
            edit_button = matching_row.find_element(
                By.XPATH,
                "(.//*[self::button or self::i or self::mat-icon or local-name()='svg'])[1]"
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

            time.sleep(1.5)
            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Edit button was not found for exact subject group row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def click_delete_for_exact_row(self, expected_values):
        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        matching_row = None

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in expected_values):
                matching_row = row

        if matching_row:
            delete_button = matching_row.find_element(
                By.XPATH,
                "(.//*[self::button or self::i or self::mat-icon or local-name()='svg'])[2]"
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

            time.sleep(1.5)
            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Delete button was not found for exact subject group row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def confirm_delete_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, delete it!']",
            "//button[normalize-space()='Yes, Delete It!']",
            "//button[normalize-space()='Yes, delete!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'Yes')]",
            "//button[contains(normalize-space(),'OK')]",
            "//button[contains(normalize-space(),'Ok')]"
        ]

        for xpath in confirm_xpaths:
            try:
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
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

            except Exception:
                continue

        return False

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def enter_subject_group_name(self, value):
        self.enter_text(self.SUBJECT_GROUP_NAME, value)

    def select_course(self):
        return self.select_first_valid_option(
            self.COURSE,
            "course"
        )

    def select_semester(self):
        return self.select_first_valid_option(
            self.SEMESTER,
            "semester"
        )

    def select_course_and_semester(self):
        return self.select_available_course_and_semester()

    def search_subject(self, value):
        self.enter_text(self.SEARCH_SUBJECT, value)

    def select_subject(self):
        return self.select_first_available_subject_checkbox()

    def select_existing_subject(self, subject_text):
        self.clear_selected_subjects()
        return self.select_subject_checkbox_by_text(subject_text)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)
