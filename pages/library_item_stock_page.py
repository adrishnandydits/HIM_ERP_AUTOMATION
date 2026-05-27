import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class LibraryItemStockPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    BOOK_TITLE = (
        By.XPATH,
        "//label[normalize-space()='Book Title']/following::input[1]"
    )

    COURSE = (
        By.XPATH,
        "//label[normalize-space()='Select Course']/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[normalize-space()='Select Semester']/following::select[1]"
    )

    SUBJECT_NG_SELECT = (
        By.XPATH,
        "//label[normalize-space()='Select Subject']/following::ng-select[1]"
    )

    QUANTITY = (
        By.XPATH,
        "//label[normalize-space()='Quantity']/following::input[1]"
    )

    REMAINING_QUANTITY = (
        By.XPATH,
        "//label[normalize-space()='Remaining Quantity']/following::input[1]"
    )

    ISBN_NO = (
        By.XPATH,
        "//label[normalize-space()='ISBN No.']/following::input[1]"
    )

    PUBLISHER_NAME = (
        By.XPATH,
        "//label[normalize-space()='Publisher Name']/following::input[1]"
    )

    AUTHOR_NAME = (
        By.XPATH,
        "//label[normalize-space()='Author Name']/following::input[1]"
    )

    RACK_NUMBER = (
        By.XPATH,
        "//label[normalize-space()='Rack Number']/following::input[1]"
    )

    BOOK_PRICE = (
        By.XPATH,
        "//label[normalize-space()='Book Price']/following::input[1]"
    )

    FINE_PER_DAY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Fine')]/following::input[1]"
    )

    DESCRIPTION = (
        By.XPATH,
        "//input[@placeholder='Enter Description']"
    )

    SEARCH_INPUT = (
        By.XPATH,
        "//input[@placeholder='Search Or Filter']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "(//button[normalize-space()='Update'])[1]"
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

    def select_subject_by_partial_text(self, partial_text):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                ng_select = self.scroll(self.SUBJECT_NG_SELECT)

                try:
                    ng_select.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        ng_select
                    )

                time.sleep(1)

                search_input = self.driver.find_element(
                    By.XPATH,
                    "//div[@aria-expanded='true']//input[@type='text']"
                )

                try:
                    search_input.clear()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].value='';",
                        search_input
                    )

                search_input.send_keys(partial_text)

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('keyup', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                    search_input
                )

                time.sleep(1)

                options = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,'ng-option')]"
                )

                for option in options:
                    option_text = option.text.strip()

                    if option_text and partial_text.lower() in option_text.lower():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});",
                            option
                        )

                        try:
                            option.click()
                        except Exception:
                            self.driver.execute_script(
                                "arguments[0].click();",
                                option
                            )

                        time.sleep(1.5)
                        return option_text

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

        raise AssertionError(
            f"Subject option containing '{partial_text}' was not selected after waiting 30 seconds."
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

    def select_subject_fundamentals(self):
        return self.select_subject_by_partial_text(
            "FUNDAMENTALS OF A"
        )

    def enter_book_title(self, value):
        self.enter_text(self.BOOK_TITLE, value)

    def enter_quantity(self, value):
        self.enter_text(self.QUANTITY, value)

    def enter_remaining_quantity(self, value):
        self.enter_text(self.REMAINING_QUANTITY, value)

    def enter_isbn_no(self, value):
        self.enter_text(self.ISBN_NO, value)

    def enter_publisher_name(self, value):
        self.enter_text(self.PUBLISHER_NAME, value)

    def enter_author_name(self, value):
        self.enter_text(self.AUTHOR_NAME, value)

    def enter_rack_number(self, value):
        self.enter_text(self.RACK_NUMBER, value)

    def enter_book_price(self, value):
        self.enter_text(self.BOOK_PRICE, value)

    def enter_fine_per_day(self, value):
        self.enter_text(self.FINE_PER_DAY, value)

    def enter_description(self, value):
        self.enter_text(self.DESCRIPTION, value)

    def search_book(self, value):
        self.enter_text(self.SEARCH_INPUT, value)

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
            f"Edit button was not found for exact library book row. "
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
                ".//td[last()]//*[self::i or self::mat-icon or local-name()='svg'][2]"
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
            f"Delete button was not found for exact library book row. "
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