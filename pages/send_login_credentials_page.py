import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SendLoginCredentialsPage:
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

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
    )

    YES_SEND_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
        "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'send')]"
    )

    SUCCESS_POPUP = (
        By.XPATH,
        "//*[contains(normalize-space(),'Mail Sent') or contains(normalize-space(),'mail sent')]"
    )

    RESULT_TABLE = (
        By.XPATH,
        "//table"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def scroll(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))

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
            self.driver.execute_script("arguments[0].click();", element)

        time.sleep(1.2)

    def enter_text(self, locator, text):
        element = self.scroll(locator)
        element.clear()
        element.send_keys(text)
        time.sleep(0.7)

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        try:
            Select(element).select_by_visible_text(visible_text)
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

            option = (
                By.XPATH,
                f"//option[contains(normalize-space(),'{visible_text}')]"
            )

            option_element = self.wait.until(
                EC.element_to_be_clickable(option)
            )

            option_element.click()

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(1.5)

    def select_first_valid_option(self, locator, field_name, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            element = self.scroll(locator)
            select = Select(element)

            valid_options = [
                option
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "select course",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                selected_text = valid_options[0].text.strip()
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
                return selected_text

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
        )

    def wait_for_semester_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            element = self.scroll(self.SEMESTER)
            select = Select(element)

            valid_options = [
                option.text.strip()
                for option in select.options
                if option.text.strip()
                and option.text.strip().lower() not in [
                    "select",
                    "select semester"
                ]
            ]

            if len(valid_options) > 0:
                return True

            time.sleep(1)

        raise AssertionError(
            "Semester dropdown options did not load after selecting course."
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_course(self):
        try:
            self.select_by_visible_text(self.COURSE, "BBA (Hospital Management)")
            return "BBA (Hospital Management)"
        except Exception:
            return self.select_first_valid_option(
                self.COURSE,
                "course",
                timeout=25
            )

    def select_semester(self):
        self.wait_for_semester_options(timeout=25)

        try:
            self.select_by_visible_text(self.SEMESTER, "2nd Sem")
            return "2nd Sem"
        except Exception:
            return self.select_first_valid_option(
                self.SEMESTER,
                "semester",
                timeout=25
            )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def wait_for_table(self):
        self.wait.until(EC.presence_of_element_located(self.RESULT_TABLE))
        time.sleep(1)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

    def get_first_student_row_text(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.get_table_rows()

                for row in rows:
                    if row.is_displayed() and row.text.strip():
                        return " ".join(row.text.split())

            except StaleElementReferenceException:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError("No stable student row text was found.")

    def click_send_for_first_row(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.get_table_rows()

                for row in rows:
                    if not row.is_displayed() or not row.text.strip():
                        continue

                    send_buttons = row.find_elements(
                        By.XPATH,
                        ".//button[contains(normalize-space(),'Send')]"
                    )

                    if len(send_buttons) == 0:
                        continue

                    send_button = send_buttons[0]

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        send_button
                    )

                    try:
                        send_button.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", send_button)

                    time.sleep(1.2)
                    return True

            except StaleElementReferenceException:
                time.sleep(1)

            time.sleep(1)

        raise AssertionError("Stable Send button was not found in the student table.")

    def confirm_send(self):
        self.click(self.YES_SEND_BUTTON)

    def wait_for_send_confirmation_popup(self):
        self.wait.until(EC.presence_of_element_located(self.YES_SEND_BUTTON))
        time.sleep(1)

    # def wait_for_mail_sent_popup(self, timeout=30):
    #     end_time = time.time() + timeout
    #
    #     while time.time() < end_time:
    #         try:
    #             success_messages = self.driver.find_elements(
    #                 By.XPATH,
    #                 "//*[contains(normalize-space(),'Mail Sent') or contains(normalize-space(),'mail sent')]"
    #             )
    #
    #             visible_success = [
    #                 message
    #                 for message in success_messages
    #                 if message.is_displayed()
    #             ]
    #
    #             if len(visible_success) > 0:
    #                 return True
    #
    #             errors = self.driver.find_elements(
    #                 By.XPATH,
    #                 "//*[contains(text(),'failed') or contains(text(),'Failed') or contains(text(),'error') or contains(text(),'Error')]"
    #             )
    #
    #             visible_errors = [
    #                 error.text.strip()
    #                 for error in errors
    #                 if error.is_displayed() and error.text.strip()
    #             ]
    #
    #             if visible_errors:
    #                 raise AssertionError(
    #                     f"Error found while sending credentials: {visible_errors}"
    #                 )
    #
    #         except StaleElementReferenceException:
    #             pass
    #
    #         time.sleep(1)
    #
    #     raise AssertionError(
    #         "Mail Sent success popup was not shown after confirming send credentials."
    #     )
    def wait_for_mail_sent_popup(self, timeout=40):

        wait = WebDriverWait(self.driver, timeout)

        success_xpath = (
            "//*[contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'mail sent') "
            "or contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'credentials sent') "
            "or contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'success') "
            "or contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'sent successfully')]"
        )

        error_xpath = (
            "//*[contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'failed') "
            "or contains(translate(., "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'error')]"
        )

        end_time = time.time() + timeout

        while time.time() < end_time:

            try:

                # SUCCESS CHECK
                success_elements = self.driver.find_elements(
                    By.XPATH,
                    success_xpath
                )

                for element in success_elements:

                    try:
                        if element.is_displayed():

                            text = element.text.strip()

                            if text:
                                print(f"SUCCESS MESSAGE: {text}")

                                return text

                    except Exception:
                        continue

                # ERROR CHECK
                error_elements = self.driver.find_elements(
                    By.XPATH,
                    error_xpath
                )

                visible_errors = []

                for error in error_elements:

                    try:
                        if error.is_displayed():

                            text = error.text.strip()

                            if text:
                                visible_errors.append(text)

                    except Exception:
                        continue

                if visible_errors:
                    raise AssertionError(
                        f"Error while sending credentials: "
                        f"{visible_errors}"
                    )

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        # DEBUGGING HELP
        body_text = self.driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        raise AssertionError(
            "Success popup not found.\n\n"
            f"Current page text:\n{body_text}"
        )