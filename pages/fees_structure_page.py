import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class FeesStructurePage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    COURSE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    SEMESTER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Semester')]/following::select[1]"
    )

    LAST_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Last Date')]/following::input[1]"
    )

    FEES_TYPE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Fees Type')]/following::select[1]"
    )

    AMOUNT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Amount')]/following::input[1]"
    )

    ADD_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Add']"
    )

    SAVE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Save']"
    )

    SHOW_FEES_STRUCTURE_HEADING = (
        By.XPATH,
        "//*[normalize-space()='SHOW FEES STRUCTURE']"
    )

    SHOW_COURSE = (
        By.XPATH,
        "//*[normalize-space()='SHOW FEES STRUCTURE']/following::select[1]"
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

    def click_visible_button(self, locator, button_name="button", timeout=35):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                buttons = self.driver.find_elements(*locator)

                for button in buttons:
                    try:
                        if button.is_displayed():
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                button
                            )

                            try:
                                button.click()
                            except Exception:
                                self.driver.execute_script(
                                    "arguments[0].click();",
                                    button
                                )

                            time.sleep(1.2)
                            return True

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
            f"\n{button_name} Click Failed\n"
            "--------------------------\n"
            f"Expected Result : {button_name} should be visible and clickable.\n"
            f"Actual Result   : {button_name} was not found/clicked.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

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

    def select_semester_2nd_sem(self):
        return self.select_by_visible_text(
            self.SEMESTER,
            "2nd Sem",
            field_name="semester",
            timeout=35
        )

    def select_fees_type_admission_fees(self):
        return self.select_by_visible_text(
            self.FEES_TYPE,
            "Admission fees",
            field_name="fees type",
            timeout=35
        )

    def select_show_course_bba(self):
        end_time = time.time() + 35
        last_options = []

        while time.time() < end_time:
            try:
                element = self.scroll(self.SHOW_COURSE)
                select = Select(element)

                selected_text = select.first_selected_option.text.strip()

                if "BBA" in selected_text and "Hospital" in selected_text:
                    return selected_text

                option_texts = [
                    option.text.strip()
                    for option in select.options
                    if option.text.strip()
                ]

                last_options = option_texts

                for option_text in option_texts:
                    if "BBA" in option_text and "Hospital" in option_text:
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
                pass
            except Exception:
                pass

            time.sleep(1)

        page_text = ""

        try:
            page_text = self.driver.find_element(By.XPATH, "//body").text
        except Exception:
            page_text = "Unable to read page text."

        raise AssertionError(
            "\nShow Course Selection Failed\n"
            "----------------------------\n"
            "Expected Result : Show Fees Structure course should be selected.\n"
            "Actual Result   : BBA Hospital course was not found/selected in Show Fees Structure dropdown.\n\n"
            "Expected Course : BBA (Hospital Management)\n"
            f"Available Options : {last_options}\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def enter_last_date(self, value):
        self.enter_date(self.LAST_DATE, value)

    def enter_amount(self, value):
        self.enter_text(self.AMOUNT, value)

    def click_add(self):
        self.click(self.ADD_BUTTON)

    def click_save(self):
        self.click(self.SAVE_BUTTON)

    def scroll_to_show_fees_structure(self):
        try:
            self.scroll(self.SHOW_FEES_STRUCTURE_HEADING)
        except Exception:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(1)

    def search_fees_structure(self):
        self.scroll_to_show_fees_structure()
        self.select_show_course_bba()
        self.click_visible_button(
            self.SEARCH_BUTTON,
            button_name="Search Button",
            timeout=35
        )

    def confirm_save_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Save It!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'save')]",
            "//button[contains(normalize-space(),'Save')]",
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