import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class TransactionReportPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    FILTER_BY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Filter By')]/following::select[1]"
    )

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    MODE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Mode')]/following::input[1]"
    )

    STUDENT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Student')]/following::input[1]"
    )

    STUDENT_DROPDOWN = (
        By.XPATH,
        "//label[contains(normalize-space(),'Student')]/following::*[contains(@class,'select') or contains(@class,'ng-select')][1]"
    )

    STUDENT_OPTION = (
        By.XPATH,
        "//span[contains(normalize-space(),'SAROJ PRADHAN')]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
    )

    EXPORT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Export')]"
    )

    SEARCH_OR_FILTER = (
        By.XPATH,
        "//input[contains(@placeholder,'Search') or contains(@placeholder,'Filter')]"
    )

    REPORT_TABLE = (
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

        time.sleep(1.2)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_filter_by(self):
        self.select_by_visible_text(self.FILTER_BY, "Paid On")

    def enter_from_date(self, date_value):
        self.enter_date(self.FROM_DATE, date_value)

    def enter_to_date(self, date_value):
        self.enter_date(self.TO_DATE, date_value)

    def enter_mode(self, mode):
        self.enter_text(self.MODE, mode)

    def select_student(self):
        try:
            self.click_select(self.STUDENT_DROPDOWN)
            self.click_select(self.STUDENT_OPTION)
        except Exception:
            self.enter_text(self.STUDENT, "PALLAB BISAI")
            time.sleep(1)

            try:
                self.click_select(self.STUDENT_OPTION)
            except Exception:
                pass

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def click_export(self):
        self.click(self.EXPORT_BUTTON)

    def enter_search_or_filter(self, value):
        self.enter_text(self.SEARCH_OR_FILTER, value)

    def wait_for_report_table(self):
        self.wait.until(EC.presence_of_element_located(self.REPORT_TABLE))
        time.sleep(1)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

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