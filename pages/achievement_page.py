import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class AchievementPage:
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

    STUDENT_SELECT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Student')]/following::select[1]"
    )

    STUDENT_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
    )

    STUDENT_DROPDOWN = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Student')]/following::*[contains(@class,'ng-select') or contains(@class,'select')][1]"
    )

    FIRST_STUDENT_OPTION = (
        By.XPATH,
        "(//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))])[1] | (//div[contains(@class,'option') and normalize-space()!=''])[1]"
    )

    DATE = (
        By.XPATH,
        "//label[normalize-space()='Date']/following::input[1]"
    )

    AWARD_NAME = (
        By.XPATH,
        "//label[contains(normalize-space(),'Award Name')]/following::input[1]"
    )

    UPLOAD_FILE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
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

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def scroll(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))

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
            self.driver.execute_script("arguments[0].click();", element)

        time.sleep(1.2)

    def click_select(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        try:
            self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

        time.sleep(1.2)

    def enter_text(self, locator, text):
        element = self.scroll(locator)
        element.clear()
        element.send_keys(text)
        time.sleep(0.7)

    def enter_date(self, locator, date_value):
        element = self.scroll(locator)

        self.driver.execute_script(
            """
            arguments[0].value = '';
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element,
            date_value
        )

        time.sleep(0.7)

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        try:
            Select(element).select_by_visible_text(visible_text)
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

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
                    "select course",
                    "select semester",
                    "select student"
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

                time.sleep(1.5)
                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
        )

    def wait_for_student_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                dropdowns = self.driver.find_elements(
                    By.XPATH,
                    "//label[contains(normalize-space(),'Select Student')]/following::*[contains(@class,'ng-select') or contains(@class,'select')][1]"
                )

                if len(dropdowns) > 0:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        dropdowns[0]
                    )

                    try:
                        dropdowns[0].click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", dropdowns[0])

                    time.sleep(1)

                    options = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                    )

                    visible_options = [
                        option
                        for option in options
                        if option.is_displayed() and option.text.strip()
                    ]

                    if len(visible_options) > 0:
                        return True

                inputs = self.driver.find_elements(
                    By.XPATH,
                    "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
                )

                if len(inputs) > 0:
                    value = inputs[0].get_attribute("value")

                    if value and value.strip():
                        return True

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        inputs[0]
                    )

                    try:
                        inputs[0].click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", inputs[0])

                    time.sleep(1)

                    options = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                    )

                    visible_options = [
                        option
                        for option in options
                        if option.is_displayed() and option.text.strip()
                    ]

                    if len(visible_options) > 0:
                        return True

            except Exception:
                pass

            time.sleep(1)

        raise AssertionError(
            "Student options did not load after selecting course and semester."
        )

    def select_student(self):
        self.wait_for_student_options(timeout=25)

        dropdowns = self.driver.find_elements(
            By.XPATH,
            "//label[contains(normalize-space(),'Select Student')]/following::*[contains(@class,'ng-select') or contains(@class,'select')][1]"
        )

        if len(dropdowns) > 0:
            dropdown = dropdowns[0]

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                dropdown
            )

            try:
                dropdown.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", dropdown)

            time.sleep(1)

        inputs = self.driver.find_elements(
            By.XPATH,
            "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
        )

        if len(inputs) > 0:
            current_value = inputs[0].get_attribute("value")

            if current_value and current_value.strip():
                return current_value.strip()

            try:
                inputs[0].click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", inputs[0])

            time.sleep(1)

        options = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
        )

        visible_options = [
            option
            for option in options
            if option.is_displayed() and option.text.strip()
        ]

        assert len(visible_options) > 0, "No visible student option found."

        option = visible_options[0]
        selected_student = " ".join(option.text.split())

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            option
        )

        try:
            option.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", option)

        time.sleep(1.5)

        inputs = self.driver.find_elements(
            By.XPATH,
            "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
        )

        if len(inputs) > 0:
            selected_value = inputs[0].get_attribute("value")

            if selected_value and selected_value.strip():
                return selected_value.strip()

        return selected_student

    def upload_document(self, locator, file_path):
        file_path = str(Path(file_path).resolve())

        file_input = self.wait.until(
            EC.presence_of_element_located(locator)
        )

        input_type = file_input.get_attribute("type")

        assert input_type == "file", (
            f"Upload locator is not pointing to file input. "
            f"Actual input type: {input_type}"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            file_input
        )

        time.sleep(0.5)

        file_input.send_keys(file_path)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            file_input
        )

        time.sleep(1.5)

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

        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in expected_values):
                return row

        table_text = ""

        try:
            table_text = self.driver.find_element(By.XPATH, "//table//tbody").text
        except Exception:
            table_text = ""

        raise AssertionError(
            f"Exact achievement row not found. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    # def click_edit_for_exact_row(self, expected_values):
    #     self.scroll_table_to_right()
    #
    #     row = self.get_exact_row_by_values(expected_values)
    #
    #     edit_button = row.find_element(
    #         By.XPATH,
    #         "(.//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
    #     )
    #
    #     self.driver.execute_script(
    #         "arguments[0].scrollIntoView({block:'center'});",
    #         edit_button
    #     )
    #
    #     try:
    #         edit_button.click()
    #     except Exception:
    #         self.driver.execute_script("arguments[0].click();", edit_button)


    def click_edit_for_exact_row(self, expected_values):
            self.scroll_table_to_right()

            row = self.get_exact_row_by_values(expected_values)

            action_buttons = row.find_elements(
                By.XPATH,
                ".//button | .//*[local-name()='svg'] | .//mat-icon | .//i"
            )

            assert len(action_buttons) >= 2, (
                "Edit button not found in achievement row."
            )

            edit_button = action_buttons[1]

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                edit_button
            )

            try:
                edit_button.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", edit_button)

            time.sleep(1.5)



    def click_delete_for_exact_row(self, expected_values):
        self.scroll_table_to_right()

        row = self.get_exact_row_by_values(expected_values)

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
            self.driver.execute_script("arguments[0].click();", delete_button)

        time.sleep(1.2)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_course(self):
        self.select_by_visible_text(self.COURSE, "BBA (Hospital Management)")
        time.sleep(2)
        return "BBA (Hospital Management)"

    def select_semester(self):
        self.select_by_visible_text(self.SEMESTER, "2nd Sem")
        time.sleep(3)
        return "2nd Sem"

    def enter_achievement_date(self, date_value):
        self.enter_date(self.DATE, date_value)

    def enter_award_name(self, award_name):
        self.enter_text(self.AWARD_NAME, award_name)

    def upload_file(self, file_path):
        self.upload_document(self.UPLOAD_FILE, file_path)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)