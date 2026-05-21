import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class IssueItemPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ISSUE_ITEM_TAB = (
        By.XPATH,
        "(//a[normalize-space()='Issue Item'])[1]"
    )

    SHOW_ISSUED_ITEM_TAB = (
        By.XPATH,
        "(//a[normalize-space()='Show Issued Item'])[1]"
    )

    USER_TYPE = (
        By.XPATH,
        "//label[normalize-space()='Select User Type']/following::select[1]"
    )

    ISSUED_TO = (
        By.XPATH,
        "//label[normalize-space()='Issued To']/following::select[1]"
    )

    ISSUED_BY = (
        By.XPATH,
        "//label[normalize-space()='Issued By']/following::select[1]"
    )

    ISSUE_DATE = (
        By.XPATH,
        "//label[normalize-space()='Issue date']/following::input[1]"
    )

    RETURN_DATE = (
        By.XPATH,
        "//label[normalize-space()='Return date']/following::input[1]"
    )

    ITEM_CATEGORY = (
        By.XPATH,
        "//label[normalize-space()='Item Category']/following::select[1]"
    )

    ITEM = (
        By.XPATH,
        "//label[normalize-space()='Item']/following::select[1]"
    )

    AVAILABLE_QUANTITY = (
        By.XPATH,
        "//label[normalize-space()='Available Quantity']/following::input[1]"
    )

    QUANTITY = (
        By.XPATH,
        "//label[normalize-space()='Quantity']/following::input[1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    RETURN_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Return']"
    )

    YES_RETURN_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Yes, return It!']"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Yes, delete It!']"
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

        input_type = element.get_attribute("type")

        assert input_type != "file", (
            f"Wrong locator used. Tried to enter text into file input. "
            f"Value: {value}"
        )

        try:
            element.clear()
        except Exception:
            self.driver.execute_script("arguments[0].value='';", element)

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

                    time.sleep(2)

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

    def select_first_valid_option(self, locator, field_name):
        invalid_options = [
            "select",
            "--select--",
            "-select-",
            "select user type",
            "issued to",
            "issued by",
            "item category",
            "item"
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

                    time.sleep(2)

                    selected_value = Select(element).first_selected_option.text.strip()

                    if selected_value and selected_value.lower() not in invalid_options:
                        return selected_value

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found or selected after waiting 30 seconds."
        )

    def select_user_type_teacher(self):
        return self.select_by_visible_text(
            self.USER_TYPE,
            "Teacher",
            "user type"
        )

    def select_issued_to(self):
        return self.select_first_valid_option(
            self.ISSUED_TO,
            "issued to"
        )

    def select_issued_by(self):
        return self.select_first_valid_option(
            self.ISSUED_BY,
            "issued by"
        )

    def select_item_category_vehicles(self):
        return self.select_by_visible_text(
            self.ITEM_CATEGORY,
            "VEHICLES",
            "item category"
        )

    def select_item_bus(self):
        return self.select_by_visible_text(
            self.ITEM,
            "BUS",
            "item"
        )

    def enter_issue_date(self, value):
        self.enter_text(self.ISSUE_DATE, value)

    def enter_return_date(self, value):
        self.enter_text(self.RETURN_DATE, value)

    def enter_quantity(self, value):
        self.enter_text(self.QUANTITY, value)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_issue_item_tab(self):
        self.click(self.ISSUE_ITEM_TAB)

    def click_show_issued_item_tab(self):
        self.click(self.SHOW_ISSUED_ITEM_TAB)

    def click_return_for_exact_row(self, expected_values):
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
            return_button = matching_row.find_element(
                By.XPATH,
                ".//button[normalize-space()='Return']"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                return_button
            )

            try:
                return_button.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    return_button
                )

            time.sleep(1.5)
            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Return button was not found for exact issue item row. "
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
            f"Delete button was not found for exact issue item row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def confirm_return(self):
        self.click(self.YES_RETURN_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)