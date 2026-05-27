import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class PreAdmissionPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_STUDENT_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Add Student')] | "
        "//a[contains(normalize-space(),'Add Student')]"
    )

    SHOW_PRE_ADMITTED_STUDENTS_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Show Pre-Admitted Students')] | "
        "//a[contains(normalize-space(),'Show Pre-Admitted Students')]"
    )

    STUDENT_ID = (
        By.XPATH,
        "//input[contains(@placeholder,'Student Id') or contains(@placeholder,'Student ID')]"
    )

    FIRST_NAME = (
        By.XPATH,
        "//input[contains(@placeholder,'First name') or contains(@placeholder,'First Name')]"
    )

    MIDDLE_NAME = (
        By.XPATH,
        "//input[contains(@placeholder,'Middle Name') or contains(@placeholder,'Middle name')]"
    )

    LAST_NAME = (
        By.XPATH,
        "//input[contains(@placeholder,'Last Name') or contains(@placeholder,'Last name')]"
    )

    GENDER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Gender')]/following::select[1]"
    )

    DATE_OF_BIRTH = (
        By.XPATH,
        "//input[@formcontrolname='dob']"
    )

    ADMISSION_DATE = (
        By.XPATH,
        "//input[@formcontrolname='admission_date']"
    )

    PHONE_NUMBER = (
        By.XPATH,
        "//input[contains(@placeholder,'Phone Number')]"
    )

    EMERGENCY_CONTACT_NUMBER = (
        By.XPATH,
        "//input[contains(@placeholder,'Emergency Contact Number')]"
    )

    MATERIAL_STATUS = (
        By.XPATH,
        "//label[contains(normalize-space(),'Material Status') or contains(normalize-space(),'Marital Status')]/following::select[1]"
    )

    RELIGION = (
        By.XPATH,
        "//label[contains(normalize-space(),'Religion')]/following::select[1]"
    )

    CASTE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Caste')]/following::select[1]"
    )

    BLOOD_GROUP = (
        By.XPATH,
        "//label[contains(normalize-space(),'Blood Group')]/following::select[1]"
    )

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Semester')]/following::select[1]"
    )

    EMAIL_ADDRESS = (
        By.XPATH,
        "//input[contains(@placeholder,'name@example.com') or contains(@placeholder,'Email') or @type='email']"
    )

    CURRENT_ADDRESS = (
        By.XPATH,
        "//input[contains(@placeholder,'Current Address')]"
    )

    PERMANENT_ADDRESS = (
        By.XPATH,
        "//input[contains(@placeholder,'Permanent Address')]"
    )

    SAVE_STUDENT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Save Student')]"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update Student']"
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
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
        "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
    )

    RESULT_TABLE = (
        By.XPATH,
        "//table"
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

    def enter_text(self, locator, text):
        element = self.scroll(locator)

        input_type = element.get_attribute("type")

        assert input_type != "file", (
            f"Wrong locator used. Tried to enter text into file input. "
            f"Value: {text}"
        )

        element.clear()
        element.send_keys(text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(0.7)

    def enter_date(self, locator, date_value):
        element = self.scroll(locator)

        converted_date = date_value

        if isinstance(date_value, str) and len(date_value.split("-")) == 3:
            first, second, third = date_value.split("-")

            if len(first) == 2 and len(second) == 2 and len(third) == 4:
                converted_date = f"{third}-{second}-{first}"

        input_type = element.get_attribute("type")

        if input_type == "date":
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];

                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                """,
                element,
                converted_date
            )
        else:
            element.clear()
            element.send_keys(date_value)

            self.driver.execute_script(
                """
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                """,
                element
            )

        time.sleep(0.8)

    def scroll_page_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.8)

    def scroll_page_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)

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
            try:
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
                        "select course",
                        "select semester",
                        "select gender",
                        "select religion",
                        "select caste",
                        "select blood group",
                        "select material status",
                        "select marital status"
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

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
        )

    def wait_for_dropdown_options(self, locator, field_name, timeout=25):
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
                    return True

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"{field_name} dropdown options did not load."
        )

    def click_add_student_tab(self):
        self.click(self.ADD_STUDENT_TAB)

    def click_show_pre_admitted_students_tab(self):
        self.click(self.SHOW_PRE_ADMITTED_STUDENTS_TAB)

    def enter_student_id(self, value):
        self.enter_text(self.STUDENT_ID, value)

    def enter_first_name(self, value):
        self.enter_text(self.FIRST_NAME, value)

    def enter_middle_name(self, value):
        self.enter_text(self.MIDDLE_NAME, value)

    def enter_last_name(self, value):
        self.enter_text(self.LAST_NAME, value)

    def enter_date_of_birth(self, value):
        self.enter_date(self.DATE_OF_BIRTH, value)

    def enter_admission_date(self, value):
        self.enter_date(self.ADMISSION_DATE, value)

    def enter_phone_number(self, value):
        self.enter_text(self.PHONE_NUMBER, value)

    def enter_emergency_contact_number(self, value):
        self.enter_text(self.EMERGENCY_CONTACT_NUMBER, value)

    def enter_email_address(self, value):
        self.enter_text(self.EMAIL_ADDRESS, value)

    def enter_current_address(self, value):
        self.enter_text(self.CURRENT_ADDRESS, value)

    def enter_permanent_address(self, value):
        self.enter_text(self.PERMANENT_ADDRESS, value)

    def select_gender(self):
        try:
            self.select_by_visible_text(self.GENDER, "Male")
            return "Male"
        except Exception:
            return self.select_first_valid_option(self.GENDER, "gender", timeout=25)

    def select_material_status(self):
        try:
            self.select_by_visible_text(self.MATERIAL_STATUS, "Single")
            return "Single"
        except Exception:
            return self.select_first_valid_option(self.MATERIAL_STATUS, "material status", timeout=25)

    def select_religion(self):
        try:
            self.select_by_visible_text(self.RELIGION, "Hinduism")
            return "Hinduism"
        except Exception:
            return self.select_first_valid_option(self.RELIGION, "religion", timeout=25)

    def select_caste(self):
        try:
            self.select_by_visible_text(self.CASTE, "General")
            return "General"
        except Exception:
            return self.select_first_valid_option(self.CASTE, "caste", timeout=25)

    def select_blood_group(self):
        try:
            self.select_by_visible_text(self.BLOOD_GROUP, "A+")
            return "A+"
        except Exception:
            return self.select_first_valid_option(self.BLOOD_GROUP, "blood group", timeout=25)

    def select_course(self):
        try:
            self.select_by_visible_text(self.COURSE, "BBA (Hospital Management)")
            return "BBA (Hospital Management)"
        except Exception:
            return self.select_first_valid_option(self.COURSE, "course", timeout=25)

    def select_semester(self):
        self.wait_for_dropdown_options(self.SEMESTER, "semester", timeout=25)

        try:
            self.select_by_visible_text(self.SEMESTER, "1st Sem")
            return "1st Sem"
        except Exception:
            return self.select_first_valid_option(self.SEMESTER, "semester", timeout=25)

    def click_save_student(self):
        self.click(self.SAVE_STUDENT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def enter_search_or_filter(self, value):
        self.enter_text(self.SEARCH_OR_FILTER, value)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

    def get_exact_row_by_values(self, expected_values, timeout=25):
        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.get_table_rows()

                for row in rows:
                    row_text = " ".join(row.text.lower().split())

                    if all(value in row_text for value in expected_values):
                        return row

            except StaleElementReferenceException:
                time.sleep(1)

            time.sleep(1)

        table_text = ""

        try:
            table_text = self.driver.find_element(By.XPATH, "//table//tbody").text
        except Exception:
            table_text = ""

        raise AssertionError(
            f"Exact pre-admission row not found. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def click_edit_for_exact_row(self, expected_values):
        self.scroll_table_to_right()

        row = self.get_exact_row_by_values(expected_values)

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

        time.sleep(1.5)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)