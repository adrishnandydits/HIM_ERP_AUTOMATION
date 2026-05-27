import time
import random

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class CollectFeesPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    COURSE = (
        By.XPATH,
        "//select[@formcontrolname='course_id']"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search']"
    )

    COLLECT_FEES_BUTTON = (
        By.XPATH,
        "//*[self::button or self::a][contains(normalize-space(),'Collect Fees')]"
    )

    FEES_CHECKBOX = (
        By.XPATH,
        "(//input[@type='checkbox'])[5]"
    )

    TRANSACTION_ID = (
        By.XPATH,
        "//input[@placeholder='Enter Transaction Id']"
    )

    PAYMENT_DATE = (
        By.XPATH,
        "//input[@placeholder='Enter Payment Date']"
    )

    RECEIVED_DATE = (
        By.XPATH,
        "//input[@placeholder='Enter Received Date']"
    )

    PAYMENT_MODE = (
        By.XPATH,
        "//select[@name='paymentMode']"
    )

    BANK = (
        By.XPATH,
        "//select[@name='bankField']"
    )

    BATCH_NUMBER = (
        By.XPATH,
        "//input[@placeholder='Enter Batch Number']"
    )

    BENEFICIARY_BANK_NAME = (
        By.XPATH,
        "//select[@name='benificiary_bank_name']"
    )

    BENEFICIARY_BRANCH_NAME = (
        By.XPATH,
        "//select[@name='benificiary_branch']"
    )

    CALCULATE_TOTAL_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Calculate Total']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    YES_SAVE_IT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Yes, Save It!']"
    )

    PRINT_LATEST_PAYMENT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Print Latest Payment']"
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

    def click_visible_element(self, locator, element_name="element", timeout=35):
        end_time = time.time() + timeout

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

                            try:
                                element.click()
                            except Exception:
                                self.driver.execute_script(
                                    "arguments[0].click();",
                                    element
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
            f"\n{element_name} Click Failed\n"
            "-----------------------------\n"
            f"Expected Result : {element_name} should be visible and clickable.\n"
            f"Actual Result   : {element_name} was not found/clicked.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

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

    def enter_date(self, locator, value):
        element = self.scroll(locator)

        try:
            element.clear()
            element.send_keys(str(value))
        except Exception:
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                """,
                element,
                str(value)
            )

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(0.8)

    def select_by_visible_text(self, locator, visible_text, field_name="dropdown", timeout=30):
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

    def select_first_valid_option(self, locator, field_name="dropdown", timeout=30):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                element = self.scroll(locator)
                select = Select(element)

                valid_options = [
                    option
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in [
                        "select",
                        "--select--",
                        "-select-",
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

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
        )

    def select_course_bba(self):
        try:
            return self.select_by_visible_text(
                self.COURSE,
                "BBA (Hospital Management)",
                field_name="course",
                timeout=30
            )
        except Exception:
            return self.select_first_valid_option(
                self.COURSE,
                field_name="course",
                timeout=30
            )

    def click_search(self):
        self.click_visible_element(
            self.SEARCH_BUTTON,
            element_name="Search Button",
            timeout=35
        )

    def wait_for_collect_fees_button(self, timeout=35):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                collect_buttons = self.driver.find_elements(*self.COLLECT_FEES_BUTTON)

                for collect_button in collect_buttons:
                    try:
                        if collect_button.is_displayed():
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                collect_button
                            )
                            return True

                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue

                body_text = " ".join(
                    self.driver.find_element(By.XPATH, "//body").text.lower().split()
                )

                assert "no data" not in body_text, (
                    "No data found after searching collect fees."
                )

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
            "\nCollect Fees Button Not Found\n"
            "-----------------------------\n"
            "Expected Result : Collect Fees button should be visible after searching course.\n"
            "Actual Result   : Collect Fees button was not found after search.\n\n"
            "Possible Reason :\n"
            "1. Selected course has no payable/unpaid student record.\n"
            "2. Collect Fees button text/class changed in the UI.\n"
            "3. Search result table did not load properly.\n"
            "4. Student fee is already paid, so Collect Fees button is not shown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def click_collect_fees(self):
        self.click_visible_element(
            self.COLLECT_FEES_BUTTON,
            element_name="Collect Fees Button",
            timeout=35
        )

    def click_fees_checkbox(self):
        checkbox = self.scroll(self.FEES_CHECKBOX)

        if not checkbox.is_selected():
            try:
                checkbox.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    checkbox
                )

        time.sleep(1)

    def enter_transaction_id(self, transaction_id):
        self.enter_text(self.TRANSACTION_ID, transaction_id)

    def enter_payment_date(self, payment_date):
        self.enter_date(self.PAYMENT_DATE, payment_date)

    def enter_received_date(self, received_date):
        self.enter_date(self.RECEIVED_DATE, received_date)

    def select_payment_mode_cash(self):
        return self.select_by_visible_text(
            self.PAYMENT_MODE,
            "UPI",
            field_name="payment mode",
            timeout=30
        )

    def select_bank_allahabad_bank(self):
        return self.select_by_visible_text(
            self.BANK,
            "Allahabad Bank",
            field_name="bank",
            timeout=30
        )

    def enter_batch_number(self, batch_number):
        self.enter_text(self.BATCH_NUMBER, batch_number)

    def select_beneficiary_bank_state_bank_of_india(self):
        return self.select_by_visible_text(
            self.BENEFICIARY_BANK_NAME,
            "State Bank Of India",
            field_name="beneficiary bank name",
            timeout=30
        )

    def select_beneficiary_branch_haldia(self):
        return self.select_by_visible_text(
            self.BENEFICIARY_BRANCH_NAME,
            "Haldia",
            field_name="beneficiary branch name",
            timeout=30
        )

    def click_calculate_total(self):
        self.click(self.CALCULATE_TOTAL_BUTTON)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_yes_save_it(self):
        self.click(self.YES_SAVE_IT_BUTTON)

    def click_print_latest_payment(self):
        before_handles = self.driver.window_handles

        self.click(self.PRINT_LATEST_PAYMENT_BUTTON)

        time.sleep(2)

        after_handles = self.driver.window_handles

        if len(after_handles) > len(before_handles):
            new_window = list(set(after_handles) - set(before_handles))[0]
            self.driver.switch_to.window(new_window)
            time.sleep(1)
            self.driver.close()
            self.driver.switch_to.window(before_handles[0])

        time.sleep(1)

    def wait_for_collect_fees_popup(self, timeout=30):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                body_text = " ".join(
                    self.driver.find_element(*self.BODY).text.lower().split()
                )

                if (
                    "payment for" in body_text
                    and "transaction id" in body_text
                    and "payment date" in body_text
                ):
                    return True

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError("Collect Fees payment form did not open.")

    def wait_for_yes_save_it_popup(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                buttons = self.driver.find_elements(*self.YES_SAVE_IT_BUTTON)

                for button in buttons:
                    if button.is_displayed():
                        return True

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError("Yes, Save It confirmation button was not displayed.")

    def wait_for_paid_status(self, timeout=35):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                body_text = " ".join(
                    self.driver.find_element(*self.BODY).text.lower().split()
                )

                if "paid" in body_text:
                    return True

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        raise AssertionError("Payment status did not change to Paid.")

    def verify_payment_status_paid_for_selected_row(self, timeout=35):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

                for row in rows:
                    row_text = " ".join(row.text.lower().split())

                    if "paid" in row_text:
                        return True

            except StaleElementReferenceException:
                pass
            except Exception:
                pass

            time.sleep(1)

        body_text = self.driver.find_element(By.XPATH, "//body").text

        raise AssertionError(
            f"Payment status was not changed to Paid. Actual page text: {body_text}"
        )

    def generate_transaction_id(self):
        return f"TXN{random.randint(100000, 999999)}"

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)