import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BookListPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    SEARCH_INPUT = (
        By.XPATH,
        "//input[@placeholder='Search Or Filter']"
    )

    DOWNLOAD_BUTTON = (
        By.XPATH,
        "//mat-icon[@role='img'][normalize-space()='cloud_download']"
        "|//*[contains(@class,'cloud') or contains(@class,'download')]"
    )

    TABLE_ROWS = (
        By.XPATH,
        "//table//tbody//tr"
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

    def search_book(self, value):
        self.enter_text(self.SEARCH_INPUT, value)

    def click_download_button(self):
        before_handles = self.driver.window_handles

        download_button = self.wait.until(
            EC.presence_of_element_located(self.DOWNLOAD_BUTTON)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            download_button
        )

        assert download_button.is_displayed(), (
            "Book list download button was found but it is not visible."
        )

        try:
            self.wait.until(EC.element_to_be_clickable(self.DOWNLOAD_BUTTON))
            download_button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                download_button
            )

        time.sleep(2)

        after_handles = self.driver.window_handles

        assert len(after_handles) >= len(before_handles), (
            "Download button was clicked, but browser window state became invalid."
        )

        return True

    def get_table_text(self):
        table = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        return table.text

    def verify_books_table_loaded(self):
        rows = self.driver.find_elements(*self.TABLE_ROWS)

        assert len(rows) > 0, (
            "Book List table has no records."
        )

        table_text = self.get_table_text().lower()

        assert "book name" in table_text, (
            f"Book Name column was not found. Actual table text: {table_text}"
        )

        assert "author name" in table_text, (
            f"Author Name column was not found. Actual table text: {table_text}"
        )

        assert "publisher name" in table_text, (
            f"Publisher Name column was not found. Actual table text: {table_text}"
        )

        assert "rack no" in table_text, (
            f"Rack No column was not found. Actual table text: {table_text}"
        )

        assert "book price" in table_text, (
            f"Book Price column was not found. Actual table text: {table_text}"
        )

        assert "sbin no" in table_text or "isbn no" in table_text, (
            f"SBIN/ISBN No column was not found. Actual table text: {table_text}"
        )

        return True

    def verify_search_result(self, expected_text):
        expected_text = str(expected_text).lower().strip()

        end_time = time.time() + 30

        while time.time() < end_time:
            rows = self.driver.find_elements(*self.TABLE_ROWS)

            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if expected_text in row_text:
                    return True

            time.sleep(1)

        table_text = self.get_table_text()

        raise AssertionError(
            f"Book search result not found after waiting 30 seconds. "
            f"Expected text: {expected_text}. "
            f"Actual table text: {table_text}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)