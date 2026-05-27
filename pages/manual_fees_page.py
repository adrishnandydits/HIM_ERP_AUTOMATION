import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class ManualFeesPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_MANUAL_FEES_TAB = (
        By.XPATH,
        "//button[normalize-space()='Add Manual Fees']"
        "|//a[normalize-space()='Add Manual Fees']"
    )

    SHOW_MANUAL_FEES_TAB = (
        By.XPATH,
        "//button[normalize-space()='Show Manual Fees']"
        "|//a[normalize-space()='Show Manual Fees']"
    )

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Semester')]/following::select[1]"
    )

    STUDENT_DROPDOWN = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Student')]/following::ng-select[1]"
    )

    STUDENT_INPUT = (
        By.XPATH,
        "//div[@aria-expanded='true']//input[@type='text']"
    )

    DATE_OF_PAYMENT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Date of Payment')]/following::input[1]"
    )

    AMOUNT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Amount')]/following::input[1]"
    )

    FILE_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Upload Slip')]/following::input[@type='file'][1]"
    )

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    SHOW_MANUAL_FEES_SUBMIT_BUTTON = (By.XPATH, "(//button[@class='btn btn-primary me-1'][normalize-space()='Submit'])[1]")

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

    def enter_date(self, locator, date_value):
        element = self.scroll(locator)

        converted_date = date_value

        if isinstance(date_value, str) and len(date_value.split("-")) == 3:
            first, second, third = date_value.split("-")

            if len(first) == 2 and len(second) == 2 and len(third) == 4:
                converted_date = f"{third}-{second}-{first}"

        input_type = element.get_attribute("type")

        if input_type == "date":
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];

                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                """,
                element,
                converted_date
            )
        else:
            element.clear()
            element.send_keys(date_value)

            self.driver.execute_script(
                """
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
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
                    return visible_text

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

    def select_semester_2nd_sem(self):
        return self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem",
            field_name="semester",
            timeout=35
        )

    def wait_for_student_options(self, timeout=35):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.STUDENT_DROPDOWN)
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    ng_select
                )

                try:
                    ng_select.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        ng_select
                    )

                time.sleep(1.5)

                options = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                )

                visible_options = [
                    option
                    for option in options
                    if option.is_displayed() and option.text.strip()
                ]

                if len(visible_options) > 0:
                    return True

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
            "\nStudent Options Load Failed\n"
            "---------------------------\n"
            "Expected Result : Student dropdown options should load after selecting course and semester.\n"
            "Actual Result   : No student option was visible in Select Student dropdown.\n\n"
            "Possible Reason :\n"
            "1. Course or semester student list is empty.\n"
            "2. Student dropdown did not open properly.\n"
            "3. Student API did not load data.\n"
            "4. Page loader or overlay blocked the dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def select_student_by_name(self, student_name, timeout=35):
        end_time = time.time() + timeout
        expected_name = " ".join(student_name.lower().split())

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.STUDENT_DROPDOWN)
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    ng_select
                )

                try:
                    ng_select.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        ng_select
                    )

                time.sleep(1.5)

                student_options = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                )

                for student_option in student_options:
                    try:
                        option_text = " ".join(student_option.text.split())

                        if (
                            student_option.is_displayed()
                            and option_text
                            and expected_name in option_text.lower()
                        ):
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                student_option
                            )

                            try:
                                student_option.click()
                            except Exception:
                                self.driver.execute_script(
                                    "arguments[0].click();",
                                    student_option
                                )

                            time.sleep(1.5)

                            page_text = " ".join(
                                self.driver.find_element(By.XPATH, "//body").text.split()
                            )

                            assert expected_name in page_text.lower(), (
                                f"Student was clicked but not selected. "
                                f"Expected student: {student_name}. "
                                f"Clicked option: {option_text}. "
                                f"Actual page text: {page_text}"
                            )

                            return option_text

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
            "\nStudent Selection Failed\n"
            "------------------------\n"
            "Expected Result : Student should be clicked and selected from Select Student dropdown.\n"
            "Actual Result   : Student option was not clicked/selected.\n\n"
            f"Student Name    : {student_name}\n\n"
            "Possible Reason :\n"
            "1. Student name is not available for selected course and semester.\n"
            "2. Student option text contains extra data.\n"
            "3. Dropdown opened but option was not visible/clickable.\n"
            "4. Page loader or overlay blocked the dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def enter_date_of_payment(self, value):
        self.enter_date(self.DATE_OF_PAYMENT, value)

    def enter_amount(self, value):
        self.enter_text(self.AMOUNT, value)

    def upload_slip(self, file_path):
        file_path = str(Path(file_path).resolve())

        file_input = self.wait.until(
            EC.presence_of_element_located(self.FILE_INPUT)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            file_input
        )

        file_input.send_keys(file_path)

        time.sleep(2)

        assert Path(file_path).exists(), (
            f"Manual fees upload slip file path does not exist: {file_path}"
        )

        return True

    def enter_from_date(self, value):
        self.enter_date(self.FROM_DATE, value)

    def enter_to_date(self, value):
        self.enter_date(self.TO_DATE, value)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_show_manual_fees_submit(self):
        self.click(self.SHOW_MANUAL_FEES_SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def click_add_manual_fees(self):
        self.click(self.ADD_MANUAL_FEES_TAB)

    def click_show_manual_fees(self):
        self.click(self.SHOW_MANUAL_FEES_TAB)

    def search_manual_fees(self, from_date, to_date):
        self.enter_from_date(from_date)
        self.enter_to_date(to_date)
        self.click_show_manual_fees_submit()

    def click_download_for_exact_row(self, expected_values):
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

            download_button = matching_row.find_element(
                By.XPATH,
                ".//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download') "
                "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download') "
                "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cloud') "
                "or self::a or self::button or self::i or self::mat-icon or local-name()='svg'][1]"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                download_button
            )

            try:
                download_button.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    download_button
                )

            time.sleep(2)

            after_handles = self.driver.window_handles

            assert len(after_handles) >= len(before_handles), (
                "Download link/icon was clicked, but browser window state became invalid."
            )

            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Download link/icon was not found for exact manual fees row. "
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
            f"Edit button was not found for exact manual fees row. "
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
            f"Delete button was not found for exact manual fees row. "
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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)