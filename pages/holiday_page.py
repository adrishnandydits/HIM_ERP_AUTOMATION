import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class HolidayPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Date')]/following::input[1]"
    )

    DESCRIPTION = (
        By.XPATH,
        "(//input[@placeholder='Enter Description'])[1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "(//button[normalize-space()='Submit'])[1]"
    )

    YEAR_DATE_SELECT = (
        By.XPATH,
        "//div[contains(.,'HOLIDAY FOR WHOLE YEAR')]//label[contains(normalize-space(),'Select Date')]/following::select[1]"
    )

    YEAR_DESCRIPTION = (
        By.XPATH,
        "(//input[@placeholder='Enter Description'])[2]"
    )

    YEAR_SUBMIT_BUTTON = (
        By.XPATH,
        "(//button[normalize-space()='Submit'])[2]"
    )

    MONTH_SELECT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Month')]/following::select[1]"
    )

    MONTH_SUBMIT_BUTTON = (
        By.XPATH,
        "(//button[normalize-space()='Submit'])[last()]"
    )

    EDIT_BUTTON = (
        By.XPATH,
        "(//table//tbody//tr[1]//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
    )

    DELETE_BUTTON = (
        By.XPATH,
        "(//table//tbody//tr[1]//*[local-name()='svg' or self::i or self::button or self::mat-icon])[last()]"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def enter_holiday_date(self, date_value):
        self.enter_date(self.DATE, date_value)

    def enter_description(self, description):
        self.enter_text(self.DESCRIPTION, description)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def select_year_date(self):
        self.select_by_visible_text(self.YEAR_DATE_SELECT, "Sunday")

    def enter_year_description(self, description):
        self.enter_text(self.YEAR_DESCRIPTION, description)

    def click_year_submit(self):
        self.click(self.YEAR_SUBMIT_BUTTON)

    def select_month(self):
        self.select_by_visible_text(self.MONTH_SELECT, "January")

    def click_month_submit(self):
        self.click(self.MONTH_SUBMIT_BUTTON)

    def click_edit(self):
        self.scroll_table_to_right()
        self.click(self.EDIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_delete(self):
        self.scroll_table_to_right()
        self.click(self.DELETE_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)