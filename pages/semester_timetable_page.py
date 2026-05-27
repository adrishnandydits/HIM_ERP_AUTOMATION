# pages/semester_timetable_page.py

import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SemesterTimetablePage:

    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(normalize-space(),'Login')]")

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

    TIMETABLE_SECTION = (
        By.XPATH,
        "//*[contains(normalize-space(),'SEMESTER TIME TABLE')]"
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
            self.wait.until(
                EC.element_to_be_clickable(locator)
            )

            element.click()

        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

        time.sleep(1)

    def enter_text(self, locator, text):
        element = self.scroll(locator)

        element.clear()
        element.send_keys(text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element
        )

        time.sleep(0.8)

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        Select(element).select_by_visible_text(visible_text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element
        )

        time.sleep(1)

    def select_first_valid_option(self, locator, field_name, timeout=25):

        end_time = time.time() + timeout

        while time.time() < end_time:

            try:
                element = self.scroll(locator)

                select = Select(element)

                valid_options = [
                    option.text.strip()
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in [
                        "select",
                        "--select--",
                        f"select {field_name.lower()}"
                    ]
                ]

                if len(valid_options) > 0:

                    selected_text = valid_options[0]

                    select.select_by_visible_text(selected_text)

                    self.driver.execute_script(
                        """
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        """,
                        element
                    )

                    time.sleep(1)

                    return selected_text

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"{field_name} dropdown options did not load."
        )

    def select_course(self):

        try:
            self.select_by_visible_text(
                self.COURSE,
                "BBA (Hospital Management)"
            )

            return "BBA (Hospital Management)"

        except Exception:

            return self.select_first_valid_option(
                self.COURSE,
                "course"
            )

    def select_semester(self):

        try:
            self.select_by_visible_text(
                self.SEMESTER,
                "1st Sem"
            )

            return "1st Sem"

        except Exception:

            return self.select_first_valid_option(
                self.SEMESTER,
                "semester"
            )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def wait_for_timetable_result(self, timeout=30):

        end_time = time.time() + timeout

        while time.time() < end_time:

            try:
                body_text = " ".join(
                    self.driver.find_element(
                        By.TAG_NAME,
                        "body"
                    ).text.lower().split()
                )

                days = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday"
                ]

                day_count = sum(
                    1
                    for day in days
                    if day in body_text
                )

                subject_cards = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(text(),'Room:')]"
                )

                visible_cards = [
                    card
                    for card in subject_cards
                    if card.is_displayed()
                ]

                if day_count >= 5 and len(visible_cards) > 0:
                    return True

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            "Semester timetable result did not load."
        )

    def get_page_text(self):

        return " ".join(
            self.driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower().split()
        )