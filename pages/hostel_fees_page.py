import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class HostelFeesPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    TYPE = (
        By.XPATH,
        "//label[normalize-space()='Type']/following::select[1]"
    )

    AMOUNT = (
        By.XPATH,
        "//input[@placeholder='Enter Amount']"
    )

    DESCRIPTION = (
        By.XPATH,
        "//input[@placeholder='Enter Description']"
    )

    GRANT_SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Choose Semester to Grant Hostel')]/following::select[1]"
    )

    STUDENT_SEARCH_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Search']/following::input[1]"
    )

    TABLE_SEARCH_INPUT = (
        By.XPATH,
        "//input[@placeholder='Search Or Filter']"
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

    BODY = (
        By.XPATH,
        "//body"
    )

    def __init__(self, driver, timeout=25):
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
            f"Wrong locator used. Tried to enter text into file input. Value: {value}"
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

        time.sleep(0.8)

    def select_by_visible_text(
        self,
        locator,
        visible_text,
        field_name="dropdown",
        timeout=35
    ):
        end_time = time.time() + timeout

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
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError(
            f"{field_name} option '{visible_text}' was not found."
        )

    def select_course_bba(self):
        return self.select_by_visible_text(
            self.COURSE,
            "BBA (Hospital Management)",
            field_name="course",
            timeout=35
        )

    def select_type_hostel_fees(self):
        return self.select_by_visible_text(
            self.TYPE,
            "Hostel Fees",
            field_name="type",
            timeout=35
        )

    def select_grant_semester_2nd_sem(self):
        return self.select_by_visible_text(
            self.GRANT_SEMESTER,
            "2nd Sem",
            field_name="grant semester",
            timeout=35
        )

    def enter_amount(self, value):
        self.enter_text(self.AMOUNT, value)

    def enter_description(self, value):
        self.enter_text(self.DESCRIPTION, value)

    def search_student(self, student_name):
        self.enter_text(self.STUDENT_SEARCH_INPUT, student_name)

    def select_student_checkbox_by_name(self, student_name, timeout=35):
        end_time = time.time() + timeout
        expected_name = " ".join(student_name.lower().split())

        while time.time() < end_time:
            try:
                self.search_student(student_name)

                checkboxes = self.driver.find_elements(
                    By.XPATH,
                    "//input[@type='checkbox']"
                )

                for checkbox in checkboxes:
                    try:
                        checkbox_text = self.driver.execute_script(
                            """
                            let element = arguments[0];

                            for (let i = 0; i < 6 && element; i++) {
                                if (element.innerText && element.innerText.trim()) {
                                    return element.innerText;
                                }

                                element = element.parentElement;
                            }

                            return '';
                            """,
                            checkbox
                        )

                        checkbox_text = " ".join(str(checkbox_text).split())

                        if expected_name in checkbox_text.lower():
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                checkbox
                            )

                            if not checkbox.is_selected():
                                try:
                                    checkbox.click()
                                except Exception:
                                    self.driver.execute_script(
                                        "arguments[0].click();",
                                        checkbox
                                    )

                            time.sleep(1)

                            assert checkbox.is_selected(), (
                                f"Student checkbox was clicked but not selected. "
                                f"Expected student: {student_name}. "
                                f"Checkbox text: {checkbox_text}"
                            )

                            return checkbox_text

                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

        page_text = ""

        try:
            page_text = self.driver.find_element(By.XPATH, "//body").text
        except Exception:
            page_text = "Unable to read page text."

        raise AssertionError(
            "\nHostel Fees Student Checkbox Selection Failed\n"
            "---------------------------------------------\n"
            "Expected Result : Student checkbox should be clicked and selected.\n"
            "Actual Result   : Student checkbox was not selected.\n\n"
            f"Student Name    : {student_name}\n\n"
            "Possible Reason :\n"
            "1. Student name is not available for selected course and semester.\n"
            "2. Student list did not load properly.\n"
            "3. Student search did not filter the list.\n"
            "4. Page loader or overlay blocked the checkbox.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def search_hostel_fees_table(self, value):
        self.enter_text(self.TABLE_SEARCH_INPUT, value)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

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
                ".//td[last()]//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'pencil') "
                "or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or self::i or self::mat-icon or local-name()='svg'][1]"
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
            f"Edit button was not found for exact hostel fees row. "
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
            f"Delete button was not found for exact hostel fees row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def confirm_delete_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, delete It!']",
            "//button[normalize-space()='Yes, delete it!']",
            "//button[normalize-space()='Yes, Delete It!']",
            "//button[normalize-space()='Yes, delete!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'Yes')]",
            "//button[contains(normalize-space(),'delete')]",
            "//button[contains(normalize-space(),'Delete')]",
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
            "Confirmation button was not clicked. "
            "Expected button like 'Yes, delete It!' but no matching clickable button was found.\n"
            f"Actual page text:\n{modal_text}"
        )

    def confirm_update_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Save It!']",
            "//button[normalize-space()='Yes, update it!']",
            "//button[normalize-space()='Yes, Update It!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'save')]",
            "//button[contains(normalize-space(),'Save')]",
            "//button[contains(normalize-space(),'update')]",
            "//button[contains(normalize-space(),'Update')]",
            "//button[contains(normalize-space(),'OK')]",
            "//button[contains(normalize-space(),'Ok')]"
        ]

        for xpath in confirm_xpaths:
            try:
                confirm_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    confirm_button
                )

                try:
                    WebDriverWait(self.driver, 3).until(
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

        return False

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)