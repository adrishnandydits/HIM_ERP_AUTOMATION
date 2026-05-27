import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class EducationQualificationPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_EDUCATION_QUALIFICATION_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Add Education Qualification')] | "
        "//a[contains(normalize-space(),'Add Education Qualification')]"
    )

    SHOW_EDUCATION_QUALIFICATION_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Show Education Qualification')] | "
        "//a[contains(normalize-space(),'Show Education Qualification')]"
    )

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

    CLASS_10_BOARD = (
        By.XPATH,
        "(//input[contains(@placeholder,'Board') or contains(@placeholder,'counsil') or contains(@placeholder,'Counsil')])[1]"
    )

    CLASS_10_MARKS = (
        By.XPATH,
        "(//input[contains(@placeholder,'Marks Obtained')])[1]"
    )

    CLASS_10_PERCENTAGE = (
        By.XPATH,
        "(//input[contains(@placeholder,'Percentage')])[1]"
    )

    CLASS_10_DIVISION = (
        By.XPATH,
        "(//input[contains(@placeholder,'Division') or contains(@placeholder,'Class')])[1]"
    )

    CLASS_10_MAIN_SUBJECT = (
        By.XPATH,
        "(//input[contains(@placeholder,'Main Subject')])[1]"
    )

    CLASS_10_YEAR = (
        By.XPATH,
        "(//input[contains(@placeholder,'Year of passing') or contains(@placeholder,'Year Of Passing')])[1]"
    )

    CLASS_12_BOARD = (
        By.XPATH,
        "(//input[contains(@placeholder,'Board') or contains(@placeholder,'counsil') or contains(@placeholder,'Counsil')])[2]"
    )

    CLASS_12_MARKS = (
        By.XPATH,
        "(//input[contains(@placeholder,'Marks Obtained')])[2]"
    )

    CLASS_12_PERCENTAGE = (
        By.XPATH,
        "(//input[contains(@placeholder,'Percentage')])[2]"
    )

    CLASS_12_DIVISION = (
        By.XPATH,
        "(//input[contains(@placeholder,'Division') or contains(@placeholder,'Class')])[2]"
    )

    CLASS_12_MAIN_SUBJECT = (
        By.XPATH,
        "(//input[contains(@placeholder,'Main Subject')])[2]"
    )

    CLASS_12_YEAR = (
        By.XPATH,
        "(//input[contains(@placeholder,'Year of passing') or contains(@placeholder,'Year Of Passing')])[2]"
    )

    GRADUATION_BOARD = (
        By.XPATH,
        "(//input[contains(@placeholder,'Board') or contains(@placeholder,'counsil') or contains(@placeholder,'Counsil')])[3]"
    )

    GRADUATION_MARKS = (
        By.XPATH,
        "(//input[contains(@placeholder,'Marks Obtained')])[3]"
    )

    GRADUATION_PERCENTAGE = (
        By.XPATH,
        "(//input[contains(@placeholder,'Percentage')])[3]"
    )

    GRADUATION_DIVISION = (
        By.XPATH,
        "(//input[contains(@placeholder,'Division') or contains(@placeholder,'Class')])[3]"
    )

    GRADUATION_MAIN_SUBJECT = (
        By.XPATH,
        "(//input[contains(@placeholder,'Main Subject')])[3]"
    )

    GRADUATION_YEAR = (
        By.XPATH,
        "(//input[contains(@placeholder,'Year of passing') or contains(@placeholder,'Year Of Passing')])[3]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
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

    def scroll_page_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.8)

    def scroll_page_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)

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

    def wait_for_student_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            select_elements = self.driver.find_elements(
                By.XPATH,
                "//label[contains(normalize-space(),'Select Student')]/following::select[1]"
            )

            if len(select_elements) > 0:
                try:
                    select = Select(select_elements[0])

                    valid_options = [
                        option.text.strip()
                        for option in select.options
                        if option.text.strip()
                        and option.text.strip().lower() not in [
                            "select",
                            "--select--",
                            "-select-",
                            "select student"
                        ]
                    ]

                    if len(valid_options) > 0:
                        return True
                except Exception:
                    pass

            ng_select_inputs = self.driver.find_elements(
                By.XPATH,
                "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
            )

            if len(ng_select_inputs) > 0:
                try:
                    ng_select_inputs[0].click()
                    time.sleep(1)

                    ng_options = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                    )

                    visible_options = [
                        option
                        for option in ng_options
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

    def select_course(self):
        try:
            self.select_by_visible_text(self.COURSE, "BBA (Hospital Management)")
            return "BBA (Hospital Management)"
        except Exception:
            return self.select_first_valid_option(
                self.COURSE,
                "course",
                timeout=25
            )

    def select_semester(self):
        self.wait_for_dropdown_options(self.SEMESTER, "semester", timeout=25)

        try:
            self.select_by_visible_text(self.SEMESTER, "2nd Sem")
            return "2nd Sem"
        except Exception:
            return self.select_first_valid_option(
                self.SEMESTER,
                "semester",
                timeout=25
            )

    def select_student(self):
        self.wait_for_student_options(timeout=25)

        select_elements = self.driver.find_elements(
            By.XPATH,
            "//label[contains(normalize-space(),'Select Student')]/following::select[1]"
        )

        if len(select_elements) > 0:
            try:
                select = Select(select_elements[0])

                valid_options = [
                    option
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in [
                        "select",
                        "--select--",
                        "-select-",
                        "select student"
                    ]
                ]

                assert len(valid_options) > 0, "No valid student option found."

                selected_text = valid_options[0].text.strip()
                select.select_by_visible_text(selected_text)

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                    """,
                    select_elements[0]
                )

                time.sleep(1.5)
                return selected_text

            except Exception:
                pass

        student_input = self.scroll(self.STUDENT_INPUT)

        try:
            student_input.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", student_input)

        time.sleep(1)

        ng_options = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
        )

        visible_options = [
            option
            for option in ng_options
            if option.is_displayed() and option.text.strip()
        ]

        assert len(visible_options) > 0, "No visible student option found."

        selected_student = " ".join(visible_options[0].text.split())

        try:
            visible_options[0].click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", visible_options[0])

        time.sleep(1.5)
        return selected_student

    def click_add_education_qualification_tab(self):
        self.click(self.ADD_EDUCATION_QUALIFICATION_TAB)

    def click_show_education_qualification_tab(self):
        self.click(self.SHOW_EDUCATION_QUALIFICATION_TAB)

    def enter_class_10_details(self, board, marks, percentage, division, main_subject, year):
        self.enter_text(self.CLASS_10_BOARD, board)
        self.enter_text(self.CLASS_10_MARKS, marks)
        self.enter_text(self.CLASS_10_PERCENTAGE, percentage)
        self.enter_text(self.CLASS_10_DIVISION, division)
        self.enter_text(self.CLASS_10_MAIN_SUBJECT, main_subject)
        self.enter_text(self.CLASS_10_YEAR, year)

    def enter_class_12_details(self, board, marks, percentage, division, main_subject, year):
        self.enter_text(self.CLASS_12_BOARD, board)
        self.enter_text(self.CLASS_12_MARKS, marks)
        self.enter_text(self.CLASS_12_PERCENTAGE, percentage)
        self.enter_text(self.CLASS_12_DIVISION, division)
        self.enter_text(self.CLASS_12_MAIN_SUBJECT, main_subject)
        self.enter_text(self.CLASS_12_YEAR, year)

    def enter_graduation_details(self, board, marks, percentage, division, main_subject, year):
        self.enter_text(self.GRADUATION_BOARD, board)
        self.enter_text(self.GRADUATION_MARKS, marks)
        self.enter_text(self.GRADUATION_PERCENTAGE, percentage)
        self.enter_text(self.GRADUATION_DIVISION, division)
        self.enter_text(self.GRADUATION_MAIN_SUBJECT, main_subject)
        self.enter_text(self.GRADUATION_YEAR, year)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)