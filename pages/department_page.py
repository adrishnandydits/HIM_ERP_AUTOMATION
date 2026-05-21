import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DepartmentPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    DEPARTMENT_NAME = (
        By.XPATH,
        "//input[@placeholder='Enter Department Name']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
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
            self.driver.execute_script(
                "arguments[0].value='';",
                element
            )

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

    def enter_department_name(self, value):
        self.enter_text(self.DEPARTMENT_NAME, value)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

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
                ".//td[last()]//*[self::i or self::mat-icon or local-name()='svg'][1]"
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
            f"Edit button was not found for exact department row. "
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
                "(.//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') "
                "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'trash') "
                "or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') "
                "or self::button or self::i or self::mat-icon or local-name()='svg'])[last()]"
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
            f"Delete button was not found for exact department row. "
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