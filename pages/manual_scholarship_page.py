import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class ManualScholarshipPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

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

    TYPE_OF_SCHOLARSHIP = (
        By.XPATH,
        "//label[contains(normalize-space(),'Type of Sholarship') or contains(normalize-space(),'Type of Scholarship')]/following::select[1]"
    )

    AMOUNT = (
        By.XPATH,
        "//input[@placeholder='Amount']"
    )

    SAVE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Save']"
    )

    SHOW_MANUAL_SCHOLARSHIP = (
        By.XPATH,
        "(//a[normalize-space()='Show Manual Scholarship'])[1]"
    )

    SHOW_COURSE = (
        By.XPATH,
        "//select[@formcontrolname='course_id']"
    )

    SHOW_SEMESTER = (
        By.XPATH,
        "//select[@formcontrolname='semester_id']"
    )

    SHOW_STUDENT_DROPDOWN = (
        By.XPATH,
        "//button[normalize-space()='Search']/preceding::ng-select[1]"
    )

    SHOW_STUDENT_INPUT = (
        By.XPATH,
        "//div[@aria-expanded='true']//input[@type='text']"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search']"
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
                    return visible_text

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError(
            f"{field_name} option '{visible_text}' was not found."
        )

    def select_visible_dropdown_by_text(
        self,
        locator,
        visible_text,
        field_name="dropdown",
        timeout=35
    ):
        end_time = time.time() + timeout
        last_options = []

        while time.time() < end_time:
            try:
                elements = self.driver.find_elements(*locator)

                for element in elements:
                    try:
                        if element.is_displayed():
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                element
                            )

                            select = Select(element)

                            option_texts = [
                                option.text.strip()
                                for option in select.options
                                if option.text.strip()
                            ]

                            last_options = option_texts

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
                        continue
                    except Exception:
                        continue

            except Exception:
                pass

            time.sleep(1)

        page_text = ""

        try:
            page_text = self.driver.find_element(By.XPATH, "//body").text
        except Exception:
            page_text = "Unable to read page text."

        raise AssertionError(
            f"\n{field_name.title()} Selection Failed\n"
            "--------------------------------------\n"
            f"Expected Option : {visible_text}\n"
            f"Available Options : {last_options}\n\n"
            f"Actual Result : {field_name} option '{visible_text}' was not found or selected.\n\n"
            "Possible Reason :\n"
            "1. Wrong hidden dropdown was selected earlier.\n"
            "2. Option text is different from expected value.\n"
            "3. Dropdown options did not load properly.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def select_course_bba(self):
        return self.select_by_visible_text(
            self.COURSE,
            "BBA (Hospital Management)",
            field_name="course",
            timeout=35
        )

    def select_semester_4th_sem(self):
        return self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem",
            field_name="semester",
            timeout=35
        )

    def select_show_course_bpharm(self):
        return self.select_by_visible_text(
            self.SHOW_COURSE,
            "BBA (Hospital Management)",
            field_name="show course",
            timeout=35
        )

    def select_show_semester_4th_sem(self):
        return self.select_by_visible_text(
            self.SHOW_SEMESTER,
            "2nd Sem",
            field_name="show semester",
            timeout=35
        )

    def select_type_of_scholarship(self, scholarship_type):
        return self.select_visible_dropdown_by_text(
            self.TYPE_OF_SCHOLARSHIP,
            scholarship_type,
            field_name="type of scholarship",
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

                            assert student_name in page_text, (
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

    def select_show_student_by_name(self, student_name, timeout=35):
        end_time = time.time() + timeout
        expected_name = " ".join(student_name.lower().split())

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.SHOW_STUDENT_DROPDOWN)
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

                            selected_text = " ".join(ng_select.text.split())

                            assert expected_name in selected_text.lower(), (
                                f"Show student was clicked but not selected. "
                                f"Expected student: {student_name}. "
                                f"Clicked option: {option_text}. "
                                f"Selected text: {selected_text}"
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
            "\nShow Manual Scholarship Student Selection Failed\n"
            "-----------------------------------------------\n"
            "Expected Result : Student should be clicked and selected from Show Manual Scholarship dropdown.\n"
            "Actual Result   : Student option was not clicked/selected.\n\n"
            f"Student Name    : {student_name}\n\n"
            "Possible Reason :\n"
            "1. Student name is not available in Show Manual Scholarship filter.\n"
            "2. Dropdown opened but option was not visible/clickable.\n"
            "3. Page loader or overlay blocked the dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def enter_type_of_scholarship(self, value):
        self.select_type_of_scholarship(value)

    def enter_amount(self, value):
        self.enter_text(self.AMOUNT, value)

    def click_save(self):
        self.click(self.SAVE_BUTTON)

    def click_show_manual_scholarship(self):
        self.click(self.SHOW_MANUAL_SCHOLARSHIP)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def verify_student_present_in_table(
        self,
        student_name,
        scholarship_type,
        amount,
        timeout=35
    ):
        end_time = time.time() + timeout

        expected_student = " ".join(student_name.lower().split())
        expected_type = " ".join(scholarship_type.lower().split())
        expected_amount = str(amount).lower().strip()

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

                for row in rows:
                    row_text = " ".join(row.text.lower().split())

                    if (
                        expected_student in row_text
                        and expected_type in row_text
                        and expected_amount in row_text
                    ):
                        return True

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        table_text = ""

        try:
            table_text = self.driver.find_element(By.XPATH, "//table//tbody").text
        except Exception:
            table_text = self.driver.find_element(*self.BODY).text

        raise AssertionError(
            "\nManual Scholarship Verification Failed\n"
            "-------------------------------------\n"
            f"Expected Student          : {student_name}\n"
            f"Expected Scholarship Type : {scholarship_type}\n"
            f"Expected Amount           : {amount}\n\n"
            "Actual Result             : Matching student scholarship row was not found after search.\n\n"
            f"Actual Table/Page Text:\n{table_text}"
        )

    def verify_no_validation_error(self):
        errors = self.driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
        )

        visible_errors = []

        for error in errors:
            try:
                if error.is_displayed() and error.text.strip():
                    visible_errors.append(error.text.strip())
            except StaleElementReferenceException:
                continue

        assert len(visible_errors) == 0, (
            f"Validation error found: {visible_errors}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)