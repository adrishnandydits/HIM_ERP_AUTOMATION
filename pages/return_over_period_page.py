import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ReturnOverPeriodPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    SEARCH_INPUT = (
        By.XPATH,
        "//input[@placeholder='Search Or Filter']"
    )

    TABLE_ROWS = (
        By.XPATH,
        "//table//tbody//tr"
    )

    TABLE_BODY = (
        By.XPATH,
        "//table//tbody"
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

        time.sleep(1)

    def search_return_over_period(self, value):
        self.enter_text(self.SEARCH_INPUT, value)

    def get_table_text(self):
        try:
            table = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table"))
            )

            return table.text

        except Exception:
            return self.driver.find_element(By.XPATH, "//body").text

    def verify_table_headers(self):
        page_text = " ".join(
            self.driver.find_element(By.XPATH, "//body").text.lower().split()
        )

        expected_headers = [
            "user name",
            "book name",
            "publisher",
            "author",
            "issued on",
            "return date",
            "late fine",
            "discount",
            "total fine"
        ]

        missing_headers = [
            header
            for header in expected_headers
            if header not in page_text
        ]

        assert len(missing_headers) == 0, (
            f"Return Over Period table headers are missing. "
            f"Missing headers: {missing_headers}. "
            f"Actual page text: {page_text}"
        )

        return True

    def verify_row_exists(self):
        rows = self.driver.find_elements(*self.TABLE_ROWS)

        if len(rows) > 0:
            return True

        table_text = self.get_table_text()

        raise AssertionError(
            "\nReturn Over Period Row Verification Failed\n"
            "------------------------------------------\n"
            "Expected Result : At least one row should be present in the Return Over Period table.\n"
            "Actual Result   : No rows are present in the Return Over Period table.\n\n"
            "Possible Reason :\n"
            "1. No book return is currently over period.\n"
            "2. Return Over Period data was not generated.\n"
            "3. Table data API returned empty response.\n"
            "4. Page loaded successfully, but no matching records exist.\n\n"
            f"Actual Table/Page Text:\n{table_text}"
        )

    def verify_search_result_exists(self, search_text):
        search_text = str(search_text).lower().strip()

        end_time = time.time() + 15

        while time.time() < end_time:
            rows = self.driver.find_elements(*self.TABLE_ROWS)

            if len(rows) == 0:
                break

            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if search_text in row_text:
                    return True

            time.sleep(1)

        table_text = self.get_table_text()

        raise AssertionError(
            "\nReturn Over Period Search Verification Failed\n"
            "---------------------------------------------\n"
            f"Expected Result : Search result should contain '{search_text}'.\n"
            "Actual Result   : Search result was not found in the table.\n\n"
            f"Actual Table/Page Text:\n{table_text}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)