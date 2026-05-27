import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class CautionMoneyPage:
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

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
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
        element.clear()
        element.send_keys(text)
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

                time.sleep(1.5)
                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
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
            "Semester dropdown options did not load after selecting course."
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_course(self):
        try:
            self.select_by_visible_text(self.COURSE, "Bachelor of Optometry")
            return "Bachelor of Optometry"
        except Exception:
            return self.select_first_valid_option(
                self.COURSE,
                "course",
                timeout=25
            )

    def select_semester(self):
        self.wait_for_semester_options(timeout=25)

        try:
            self.select_by_visible_text(self.SEMESTER, "2nd Sem")
            return "2nd Sem"
        except Exception:
            return self.select_first_valid_option(
                self.SEMESTER,
                "semester",
                timeout=25
            )

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def wait_for_result_table(self):
        self.wait.until(EC.presence_of_element_located(self.RESULT_TABLE))
        time.sleep(1)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

    def get_page_text(self):
        return " ".join(
            self.driver.find_element(By.XPATH, "//body").text.split()
        )