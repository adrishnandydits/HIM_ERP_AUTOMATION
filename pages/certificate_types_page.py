import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CertificateTypesPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    CERTIFICATE_TYPE_NAME = (
        By.XPATH,
        "//label[contains(normalize-space(),'Certificate Type Name')]/following::input[1]"
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

    def enter_text(self, locator, text):
        element = self.scroll(locator)
        element.clear()
        element.send_keys(text)
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
            f"Exact certificate type row not found. "
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

        time.sleep(1.2)

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

    def enter_certificate_type_name(self, certificate_type_name):
        self.enter_text(self.CERTIFICATE_TYPE_NAME, certificate_type_name)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)