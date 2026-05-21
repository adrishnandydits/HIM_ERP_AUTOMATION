import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class StaffAttendancePage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    USER_TYPE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select User Type')]/following::select[1]"
    )

    DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Date')]/following::input[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    TABLE_ROWS = (
        By.XPATH,
        "//table//tbody//tr"
    )

    FIRST_ROW_PRESENT = (
        By.XPATH,
        "(//table//tbody//tr)[1]//input[@type='radio'][1]"
    )

    FIRST_ROW_ABSENT = (
        By.XPATH,
        "(//table//tbody//tr)[1]//input[@type='radio'][2]"
    )

    FIRST_ROW_LATE = (
        By.XPATH,
        "(//table//tbody//tr)[1]//input[@type='radio'][3]"
    )

    FIRST_ROW_HALF_DAY = (
        By.XPATH,
        "(//table//tbody//tr)[1]//input[@type='radio'][4]"
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

        time.sleep(1.2)

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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_user_type(self):
        self.select_by_visible_text(self.USER_TYPE, "Teacher")

    def enter_select_date(self, date_value):
        self.enter_date(self.DATE, date_value)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def mark_first_staff_present(self):
        self.click(self.FIRST_ROW_PRESENT)

    def mark_first_staff_absent(self):
        self.click(self.FIRST_ROW_ABSENT)

    def mark_first_staff_late(self):
        self.click(self.FIRST_ROW_LATE)

    def mark_first_staff_half_day(self):
        self.click(self.FIRST_ROW_HALF_DAY)

    def mark_staff_present_by_row_number(self, row_number):
        locator = (
            By.XPATH,
            f"(//table//tbody//tr)[{row_number}]//input[@type='radio'][1]"
        )
        self.click(locator)

    def mark_staff_absent_by_row_number(self, row_number):
        locator = (
            By.XPATH,
            f"(//table//tbody//tr)[{row_number}]//input[@type='radio'][2]"
        )
        self.click(locator)

    def mark_staff_late_by_row_number(self, row_number):
        locator = (
            By.XPATH,
            f"(//table//tbody//tr)[{row_number}]//input[@type='radio'][3]"
        )
        self.click(locator)

    def mark_staff_half_day_by_row_number(self, row_number):
        locator = (
            By.XPATH,
            f"(//table//tbody//tr)[{row_number}]//input[@type='radio'][4]"
        )
        self.click(locator)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)