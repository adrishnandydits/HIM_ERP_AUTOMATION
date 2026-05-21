import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class InternshipDetailsPage:
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

    PROVIDER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Provider')]/following::select[1]"
    )

    STUDENT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Student')]/following::input[1]"
    )

    STUDENT_OPTION = (
        By.XPATH,
        "(//span[@class='ng-option-label ng-star-inserted'][contains(text(),'BISWAJIT')])[1]"
    )

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To date') or contains(normalize-space(),'To Date')]/following::input[1]"
    )

    FILE_INPUT = (
        By.XPATH,
        "//label[normalize-space()='File']/following::input[@type='file'][1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
    )

    EDIT_BUTTON = (
        By.XPATH,
        "(//table//tbody//tr[1]//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
    )

    DELETE_BUTTON = (
        By.XPATH,
        "(//table//tbody//tr[1]//*[local-name()='svg' or self::i or self::button or self::mat-icon])[last()]"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
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

    def click_select(self, locator):
        element = self.wait.until(EC.presence_of_element_located(locator))

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

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

        time.sleep(1.2)

    def enter_date(self, locator, date_value):
        element = self.scroll(locator)

        self.driver.execute_script(
            """
            arguments[0].value = '';
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element,
            date_value
        )

        time.sleep(0.7)

    def upload_file(self, file_path):
        file_path = str(Path(file_path).resolve())

        file_input = self.wait.until(
            EC.presence_of_element_located(self.FILE_INPUT)
        )

        self.driver.execute_script(
            """
            arguments[0].style.display = 'block';
            arguments[0].style.visibility = 'visible';
            arguments[0].style.opacity = 1;
            arguments[0].removeAttribute('hidden');
            arguments[0].removeAttribute('disabled');
            arguments[0].scrollIntoView({block:'center'});
            """,
            file_input
        )

        time.sleep(0.5)

        file_input.send_keys(file_path)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            file_input
        )

        time.sleep(1.5)

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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def select_course(self):
        self.select_by_visible_text(self.COURSE, "BBA")

    def select_semester(self):
        self.select_by_visible_text(self.SEMESTER, "3rd Sem")

    def select_provider(self):
        self.select_by_visible_text(self.PROVIDER, "Amazon")

    def select_student(self):
        self.click_select(self.STUDENT)
        self.click_select(self.STUDENT_OPTION)

    def enter_from_date(self, date_value):
        self.enter_date(self.FROM_DATE, date_value)

    def enter_to_date(self, date_value):
        self.enter_date(self.TO_DATE, date_value)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_edit(self):
        self.scroll_table_to_right()
        self.click(self.EDIT_BUTTON)

    def click_delete(self):
        self.scroll_table_to_right()
        self.click(self.DELETE_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)