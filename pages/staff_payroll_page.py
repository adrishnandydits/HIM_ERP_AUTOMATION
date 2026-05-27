import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class StaffPayrollPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    USER_TYPE = (
        By.XPATH,
        "//label[normalize-space()='Select User Type']/following::select[1]"
    )

    MONTH = (
        By.XPATH,
        "//label[normalize-space()='Select Month']/following::select[1]"
    )

    YEAR = (
        By.XPATH,
        "//label[normalize-space()='Select Year']/following::select[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search']"
    )

    GENERATE_PAYROLL_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Generate Payroll')]"
    )

    REVERT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Revert')]"
    )

    YES_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Yes') or contains(normalize-space(),'OK') or contains(normalize-space(),'Ok')]"
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

    def select_user_type_students(self):
        return self.select_by_visible_text(
            self.USER_TYPE,
            "Students",
            "user type"
        )

    def select_month_february(self):
        return self.select_by_visible_text(
            self.MONTH,
            "February",
            "month"
        )

    def select_year_2025(self):
        return self.select_by_visible_text(
            self.YEAR,
            "2025",
            "year"
        )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def scroll_table_to_right(self):
        self.driver.execute_script(
            """
            const elements = document.querySelectorAll('*');

            for (const el of elements) {
                if (el.scrollWidth > el.clientWidth) {
                    el.scrollLeft = el.scrollWidth;
                }
            }
            """
        )

        time.sleep(1)

    def click_generate_payroll_for_first_row(self):
        self.scroll_table_to_right()

        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        assert len(rows) > 0, (
            "Generate Payroll failed because no payroll rows were found after search."
        )

        first_row = rows[0]

        generate_button = first_row.find_element(
            By.XPATH,
            ".//*[self::button or self::i or self::mat-icon or local-name()='svg' "
            "or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'generate')]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            generate_button
        )

        try:
            generate_button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                generate_button
            )

        time.sleep(1.5)
        return True

    def click_revert_for_first_row(self):
        self.scroll_table_to_right()

        rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

        assert len(rows) > 0, (
            "Revert failed because no payroll rows were found after generate payroll."
        )

        first_row = rows[0]

        revert_button = first_row.find_element(
            By.XPATH,
            ".//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'revert') "
            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'undo') "
            "or self::button or self::i or self::mat-icon or local-name()='svg'][last()]"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            revert_button
        )

        try:
            revert_button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                revert_button
            )

        time.sleep(1.5)
        return True

    def confirm_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, Save It!']",
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Generate It!']",
            "//button[normalize-space()='Yes, generate it!']",
            "//button[normalize-space()='Yes, Revert It!']",
            "//button[normalize-space()='Yes, revert it!']",
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