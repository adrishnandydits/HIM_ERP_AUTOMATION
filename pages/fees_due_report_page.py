import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class FeesDueReportPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    FEES_DUE_REPORT_TAB = (
        By.XPATH,
        "//button[normalize-space()='Fees Due Report'] | //a[normalize-space()='Fees Due Report']"
    )

    FEES_DUE_COURSE_WISE_TAB = (
        By.XPATH,
        "//button[normalize-space()='Fees Due Course Wise'] | //a[normalize-space()='Fees Due Course Wise']"
    )

    FEES_DUE_DETAILS_TAB = (
        By.XPATH,
        "//button[normalize-space()='Fees Due Details'] | //a[normalize-space()='Fees Due Details']"
    )

    COURSE = (
        By.XPATH,
        "//select[@formcontrolname='course_id']"
    )

    SEMESTER = (
        By.XPATH,
        "//select[@formcontrolname='semester_id']"
    )

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
    )

    FETCH_REPORT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Fetch report')]"
    )

    SEARCH_OR_FILTER = (
        By.XPATH,
        "//input[contains(@placeholder,'Search') or contains(@placeholder,'Filter')]"
    )

    EXPORT_BUTTON = (
        By.XPATH,
        "//button[@title='Download']"
    )

    REPORT_TITLE = (
        By.XPATH,
        "//*[contains(normalize-space(),'DUE FEES LIST')]"
    )

    REPORT_TABLE = (
        By.XPATH,
        "//table"
    )

    CHART = (
        By.XPATH,
        "//*[name()='svg' or self::canvas]"
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

    def click_fees_due_report_tab(self):
        self.click(self.FEES_DUE_REPORT_TAB)

    def click_fees_due_course_wise_tab(self):
        self.click(self.FEES_DUE_COURSE_WISE_TAB)

    def click_fees_due_details_tab(self):
        self.click(self.FEES_DUE_DETAILS_TAB)

    def select_course(self):
        self.select_by_visible_text(self.COURSE, "BBA")

    def select_semester(self):
        self.select_by_visible_text(self.SEMESTER, "1st Sem")

    def enter_from_date(self, date_value):
        self.enter_date(self.FROM_DATE, date_value)

    def enter_to_date(self, date_value):
        self.enter_date(self.TO_DATE, date_value)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def click_fetch_report(self):
        self.click(self.FETCH_REPORT_BUTTON)

    def enter_search_or_filter(self, value):
        self.enter_text(self.SEARCH_OR_FILTER, value)

    def click_export(self):
        buttons = self.driver.find_elements(
            By.XPATH,
            "//button"
        )

        for button in buttons:
            button_text = button.text.strip().lower()
            button_html = button.get_attribute("outerHTML").lower()

            if (
                "export" in button_text
                or "download" in button_text
                or "cloud" in button_html
                or "fa-download" in button_html
                or "download" in button_html
            ):
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    button
                )

                try:
                    button.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", button)

                time.sleep(1.5)
                return True

        raise AssertionError("Export button was not found on Fees Due Report page.")

    def wait_for_report_table(self):
        self.wait.until(EC.presence_of_element_located(self.REPORT_TABLE))
        time.sleep(1)

    def wait_for_chart(self):
        self.wait.until(EC.presence_of_element_located(self.CHART))
        time.sleep(1)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

    def get_report_title_text(self):
        element = self.scroll(self.REPORT_TITLE)
        return element.text.strip()

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