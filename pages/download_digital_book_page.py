import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class DownloadDigitalBookPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    COURSE = (
        By.XPATH,
        "//label[normalize-space()='Select Course']/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[normalize-space()='Select Semester']/following::select[1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    DOWNLOAD_LINK = (
        By.XPATH,
        "//table//tbody//tr//a[contains(normalize-space(),'.pdf') or contains(@href,'.pdf')]"
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

        time.sleep(0.7)

    def select_by_visible_text(self, locator, visible_text, field_name):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                element = self.scroll(locator)
                select = Select(element)

                option_texts = [
                    option.text.strip()
                    for option in select.options
                    if option.text.strip()
                ]

                if visible_text in option_texts:
                    select.select_by_visible_text(visible_text)

                    self.driver.execute_script(
                        """
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                        """,
                        element
                    )

                    time.sleep(1.5)

                    selected_value = Select(element).first_selected_option.text.strip()

                    assert selected_value == visible_text, (
                        f"{field_name} was not selected correctly. "
                        f"Expected: {visible_text}, Actual: {selected_value}"
                    )

                    return selected_value

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"{field_name} option '{visible_text}' was not found after waiting 30 seconds."
        )

    def select_by_partial_visible_text(self, locator, partial_text, field_name):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                element = self.scroll(locator)
                select = Select(element)

                for option in select.options:
                    option_text = option.text.strip()

                    if partial_text.lower() in option_text.lower():
                        select.select_by_visible_text(option_text)

                        self.driver.execute_script(
                            """
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                            """,
                            element
                        )

                        time.sleep(1.5)

                        selected_value = Select(element).first_selected_option.text.strip()

                        assert partial_text.lower() in selected_value.lower(), (
                            f"{field_name} was not selected correctly. "
                            f"Expected text containing: {partial_text}, Actual: {selected_value}"
                        )

                        return selected_value

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"{field_name} option containing '{partial_text}' was not found after waiting 30 seconds."
        )

    def select_course_bba_hospital_management(self):
        return self.select_by_partial_visible_text(
            self.COURSE,
            "BBA (Hospital Management)",
            "course"
        )

    def select_semester_2nd_sem(self):
        return self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem",
            "semester"
        )

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_download_link_for_exact_row(self, expected_values):
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
            before_handles = self.driver.window_handles

            download_link = matching_row.find_element(
                By.XPATH,
                ".//a[contains(normalize-space(),'.pdf') or contains(@href,'.pdf')]"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                download_link
            )

            assert download_link.is_displayed(), (
                "Download PDF link was found but it is not visible."
            )

            try:
                download_link.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    download_link
                )

            time.sleep(2)

            after_handles = self.driver.window_handles

            assert len(after_handles) >= len(before_handles), (
                "Download PDF link was clicked, but browser window state became invalid."
            )

            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Download PDF link was not found for exact digital book row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)