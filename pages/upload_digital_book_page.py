import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class UploadDigitalBookPage:
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

    BOOK = (
        By.XPATH,
        "//label[normalize-space()='Select Book']/following::select[1]"
    )

    FILE_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
    )

    DOWNLOAD_ICON = (
        By.XPATH,
        "//mat-icon[@role='img'][normalize-space()='cloud_download']"
        "|//*[contains(@class,'cloud') or contains(@class,'download')]"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "// button[normalize - space() = 'Yes, save It!']"
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
                        return option_text

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"{field_name} option containing '{partial_text}' was not found after waiting 30 seconds."
        )

    def select_first_valid_option(self, locator, field_name):
        invalid_options = [
            "select",
            "--select--",
            "-select-",
            "select course",
            "select semester",
            "select book"
        ]

        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                element = self.scroll(locator)
                select = Select(element)

                valid_options = [
                    option.text.strip()
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in invalid_options
                ]

                if len(valid_options) > 0:
                    selected_text = valid_options[0]

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

                    selected_value = Select(element).first_selected_option.text.strip()

                    assert selected_value.lower() not in invalid_options, (
                        f"{field_name} was not selected correctly. "
                        f"Selected value: {selected_value}"
                    )

                    return selected_value

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting 30 seconds."
        )

    def select_course_bba_hospital_management(self):
        return self.select_by_partial_visible_text(
            self.COURSE,
            "BBA (Hospital Managem",
            "course"
        )

    def select_semester_2nd_sem(self):
        return self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem",
            "semester"
        )

    def select_book_test_book(self):
        return self.select_by_visible_text(
            self.BOOK,
            "Test Book",
            "book"
        )

    def select_course(self):
        return self.select_first_valid_option(
            self.COURSE,
            "course"
        )

    def select_semester(self):
        return self.select_first_valid_option(
            self.SEMESTER,
            "semester"
        )

    def select_book(self):
        return self.select_first_valid_option(
            self.BOOK,
            "book"
        )

    def upload_file(self, file_path):
        file_path = str(Path(file_path).resolve())

        file_input = self.wait.until(
            EC.presence_of_element_located(self.FILE_INPUT)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            file_input
        )

        file_input.send_keys(file_path)

        time.sleep(1.5)

        uploaded_value = file_input.get_attribute("value")

        assert uploaded_value != "", (
            f"Digital book file was not uploaded. File path: {file_path}"
        )

        return True

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_download_icon_for_exact_row(self, expected_values):
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

            download_icon = matching_row.find_element(
                By.XPATH,
                ".//*[self::button or self::i or self::mat-icon or local-name()='svg']"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                download_icon
            )

            assert download_icon.is_displayed(), (
                "Download icon was found in matched digital book row but it is not visible."
            )

            try:
                download_icon.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    download_icon
                )

            time.sleep(2)

            after_handles = self.driver.window_handles

            assert len(after_handles) >= len(before_handles), (
                "Download icon was clicked, but browser window state became invalid."
            )

            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Download icon was not found for exact digital book row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

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
            f"Edit button was not found for exact digital book row. "
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
                "(.//*[self::button or self::i or self::mat-icon or local-name()='svg'])[last()]"
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
            f"Delete button was not found for exact digital book row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def confirm_delete_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Save It!']",
            "//button[contains(normalize-space(),'Yes')]",
            "//button[contains(normalize-space(),'save')]",
            "//button[contains(normalize-space(),'Save')]",
            "//button[contains(normalize-space(),'OK')]",
            "//button[contains(normalize-space(),'Ok')]"
        ]

        for xpath in confirm_xpaths:
            try:
                confirm_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    confirm_button
                )

                assert confirm_button.is_displayed(), (
                    f"Delete confirmation button found but not visible. XPath: {xpath}"
                )

                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
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

        modal_text = ""

        try:
            modal_text = self.driver.find_element(By.XPATH, "//body").text
        except Exception:
            modal_text = "Unable to read page text."

        raise AssertionError(
            "Delete confirmation button was not clicked.\n"
            "Expected button text: Yes, save it!\n"
            f"Actual page/modal text:\n{modal_text}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)