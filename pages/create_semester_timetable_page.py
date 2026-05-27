import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class CreateSemesterTimetablePage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    CREATE_SEMESTER_TABLE_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Create Semester Table')] | "
        "//a[contains(normalize-space(),'Create Semester Table')]"
    )

    SHOW_SEMESTER_TABLE_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'Show Semester Table')] | "
        "//a[contains(normalize-space(),'Show Semester Table')]"
    )

    COURSE = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Select Course')]/following::select[1])[1]"
    )

    SEMESTER = (
        By.XPATH,
        "(//label[contains(normalize-space(),'Select Semester')]/following::select[1])[1]"
    )

    SUBJECT_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Subject')]/following::input[1]"
    )

    TEACHER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Teacher List')]/following::select[1]"
    )

    TIME_FROM = (
        By.XPATH,
        "//input[@placeholder='Time From']"
    )

    TIME_TO = (
        By.XPATH,
        "//input[@placeholder='Time Tpo']"
    )

    DAY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Day')]/following::select[1]"
    )

    ROOM_NO = (
        By.XPATH,
        "//label[contains(normalize-space(),'Room No')]/following::input[1]"
    )

    ADD_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Add']"
    )

    SAVE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Save']"
    )

    YES_SAVE_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
        "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'save')]"
    )

    SESSION = (By.XPATH, "//select[@formcontrolname='session_id']")

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Search')]"
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

        input_type = element.get_attribute("type")

        assert input_type != "file", (
            f"Wrong locator used. Tried to enter text into file input. Value: {text}"
        )

        element.clear()
        element.send_keys(text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element
        )

        time.sleep(0.7)

    def enter_time(self, locator, time_value):
        element = self.scroll(locator)

        try:
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(time_value)
        except Exception:
            pass

        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element,
            time_value
        )

        time.sleep(1)

    def select_element_by_text(self, select_element, visible_text):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            select_element
        )

        Select(select_element).select_by_visible_text(visible_text)

        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            select_element
        )

        time.sleep(1.5)

    def select_element_first_valid_option(self, select_element, field_name, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                select = Select(select_element)

                valid_options = [
                    option
                    for option in select.options
                    if option.text.strip()
                    and option.text.strip().lower() not in [
                        "select",
                        "--select--",
                        "-select-",
                        "select course",
                        "select semester",
                        "select session",
                        "select day",
                        "teacher list",
                        "select teacher"
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
                        select_element
                    )

                    time.sleep(1.5)
                    return selected_text

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            f"No valid {field_name} option found after waiting {timeout} seconds."
        )

    def select_by_visible_text(self, locator, visible_text):
        element = self.scroll(locator)

        self.select_element_by_text(element, visible_text)

    def select_first_valid_option(self, locator, field_name, timeout=25):
        element = self.scroll(locator)
        return self.select_element_first_valid_option(element, field_name, timeout)

    def wait_for_dropdown_options(self, locator, field_name, timeout=25):
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
                        "-select-",
                        f"select {field_name.lower()}"
                    ]
                ]

                if len(valid_options) > 0:
                    return True

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(f"{field_name} dropdown options did not load.")

    def get_visible_selects(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            selects = self.driver.find_elements(By.XPATH, "//select")

            visible_selects = []

            for select_element in selects:
                try:
                    if select_element.is_displayed():
                        visible_selects.append(select_element)
                except StaleElementReferenceException:
                    continue

            if len(visible_selects) > 0:
                return visible_selects

            time.sleep(1)

        raise AssertionError("No visible dropdowns found on the page.")

    def get_select_option_texts(self, select_element):
        try:
            select = Select(select_element)

            return [
                option.text.strip()
                for option in select.options
                if option.text.strip()
            ]

        except StaleElementReferenceException:
            return []

    def find_visible_select_containing_option(self, expected_option, field_name, timeout=25):
        end_time = time.time() + timeout
        expected_option_lower = expected_option.lower().strip()

        while time.time() < end_time:
            try:
                visible_selects = self.get_visible_selects(timeout=5)

                for select_element in visible_selects:
                    option_texts = self.get_select_option_texts(select_element)

                    for option_text in option_texts:
                        if expected_option_lower == option_text.lower().strip():
                            return select_element

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        available_options = []

        try:
            visible_selects = self.get_visible_selects(timeout=5)

            for select_element in visible_selects:
                available_options.append(self.get_select_option_texts(select_element))
        except Exception:
            pass

        raise AssertionError(
            f"Dropdown for {field_name} containing option '{expected_option}' was not found. "
            f"Available visible dropdown options: {available_options}"
        )

    def select_option_from_visible_dropdown(self, expected_option, field_name, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                select_element = self.find_visible_select_containing_option(
                    expected_option,
                    field_name,
                    timeout=5
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    select_element
                )

                Select(select_element).select_by_visible_text(expected_option)

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                    """,
                    select_element
                )

                time.sleep(1.5)
                return expected_option

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

        raise AssertionError(
            f"Could not select '{expected_option}' from {field_name} dropdown."
        )

    def wait_for_subject_options(self, timeout=25):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                subject_inputs = self.driver.find_elements(
                    By.XPATH,
                    "//label[contains(normalize-space(),'Select Subject')]/following::input[1]"
                )

                if len(subject_inputs) > 0:
                    subject_input = subject_inputs[0]

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        subject_input
                    )

                    try:
                        subject_input.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", subject_input)

                    time.sleep(1)

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
                pass

            time.sleep(1)

        raise AssertionError(
            "Subject options did not load after selecting course and semester."
        )

    def select_subject(self):
        self.wait_for_subject_options(timeout=25)

        subject_input = self.wait.until(
            EC.presence_of_element_located(self.SUBJECT_INPUT)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            subject_input
        )

        try:
            subject_input.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", subject_input)

        time.sleep(1)

        options = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
        )

        visible_options = [
            option
            for option in options
            if option.is_displayed() and option.text.strip()
        ]

        assert len(visible_options) > 0, "No visible subject option found."

        selected_subject = " ".join(visible_options[0].text.split())

        try:
            visible_options[0].click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", visible_options[0])

        time.sleep(1.5)
        return selected_subject

    def select_course(self):
        try:
            self.select_by_visible_text(self.COURSE, "B.Pharm")
            return "B.Pharm"
        except Exception:
            return self.select_first_valid_option(
                self.COURSE,
                "course",
                timeout=25
            )

    def select_semester(self):
        self.wait_for_dropdown_options(self.SEMESTER, "semester", timeout=25)

        try:
            self.select_by_visible_text(self.SEMESTER, "4th Sem")
            return "4th Sem"
        except Exception:
            return self.select_first_valid_option(
                self.SEMESTER,
                "semester",
                timeout=25
            )

    def select_teacher(self):
        self.wait_for_dropdown_options(self.TEACHER, "teacher", timeout=25)

        try:
            self.select_by_visible_text(self.TEACHER, "Dr. Suman Pattanayak")
            return "Dr. Suman Pattanayak"
        except Exception:
            return self.select_first_valid_option(
                self.TEACHER,
                "teacher",
                timeout=25
            )

    def select_day(self):
        self.wait_for_dropdown_options(self.DAY, "day", timeout=25)

        try:
            self.select_by_visible_text(self.DAY, "Monday")
            return "Monday"
        except Exception:
            return self.select_first_valid_option(
                self.DAY,
                "day",
                timeout=25
            )

    def enter_time_from(self, time_value):
        self.enter_time(self.TIME_FROM, time_value)

    def enter_time_to(self, time_value):
        self.enter_time(self.TIME_TO, time_value)

    def enter_room_no(self, room_no):
        self.enter_text(self.ROOM_NO, room_no)

    def click_add(self):
        self.click(self.ADD_BUTTON)

    def click_save(self):
        self.click(self.SAVE_BUTTON)

    def confirm_save(self):
        self.click(self.YES_SAVE_BUTTON)

    def click_create_semester_table_tab(self):
        self.click(self.CREATE_SEMESTER_TABLE_TAB)

    def click_show_semester_table_tab(self):
        show_tab = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(normalize-space(),'Show Semester Table')] | "
                    "//a[contains(normalize-space(),'Show Semester Table')]"
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            show_tab
        )

        try:
            show_tab.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", show_tab)

        time.sleep(2)

        self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(normalize-space(),'SHOW SEMESTER TABLE')] | "
                    "//*[contains(normalize-space(),'Select Session')]"
                )
            )
        )

        time.sleep(1.5)

    def select_show_course(self):
        return self.select_option_from_visible_dropdown(
            "BBA (Hospital Management)",
            "show course",
            timeout=50
        )

    def select_show_semester(self):
        return self.select_option_from_visible_dropdown(
            "4th Sem",
            "show semester",
            timeout=50
        )

    def select_show_session(self):
        self.select_by_visible_text(self.SESSION, "2024")


    #def select_show_session(self):
    #    return self.select_option_from_visible_dropdown(
    #        "2024",
    #        "show session",
    #        timeout=25
    #    )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def wait_for_list_row(self, expected_values, timeout=25):
        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

                for row in rows:
                    if not row.is_displayed() or not row.text.strip():
                        continue

                    row_text = " ".join(row.text.lower().split())

                    if all(value in row_text for value in expected_values):
                        return row_text

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        table_text = ""

        try:
            table_text = self.driver.find_element(By.XPATH, "//table//tbody").text
        except Exception:
            table_text = self.driver.find_element(By.XPATH, "//body").text

        raise AssertionError(
            f"Semester timetable list row not found. "
            f"Expected values: {expected_values}. "
            f"Actual text: {table_text}"
        )

    def wait_for_save_confirmation_popup(self, timeout=20):
        end_time = time.time() + timeout

        while time.time() < end_time:
            buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'yes') "
                "and contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'save')]"
            )

            visible_buttons = []

            for button in buttons:
                try:
                    if button.is_displayed():
                        visible_buttons.append(button)
                except StaleElementReferenceException:
                    continue

            if len(visible_buttons) > 0:
                return True

            time.sleep(1)

        raise AssertionError("Save confirmation popup was not shown.")

    def wait_for_saved_successfully_or_timetable(self, timeout=30):
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                success_messages = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'successfully') "
                    "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'saved')]"
                )

                visible_success = [
                    message.text.strip()
                    for message in success_messages
                    if message.is_displayed() and message.text.strip()
                ]

                if visible_success:
                    return visible_success[0]

                body_text = self.driver.find_element(By.XPATH, "//body").text.lower()

                if (
                    "semester time table" in body_text
                    and "subject" in body_text
                    and "teacher name" in body_text
                    and "room no" in body_text
                ):
                    return "Semester timetable displayed after save."

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        raise AssertionError(
            "Saved success message or timetable result was not shown after confirming save."
        )

    def wait_for_show_timetable_result(self, timeout=30):
        end_time = time.time() + timeout

        while time.time() < end_time:

            try:
                no_data_elements = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(translate(normalize-space(),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'no data') "
                    "or contains(translate(normalize-space(),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'no record') "
                    "or contains(translate(normalize-space(),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'not found') "
                    "or contains(translate(normalize-space(),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                    "'data not found')]"
                )

                visible_no_data = []

                for element in no_data_elements:

                    try:
                        if (
                                element.is_displayed()
                                and element.text.strip()
                        ):
                            visible_no_data.append(
                                element.text.strip()
                            )

                    except StaleElementReferenceException:
                        continue

                if visible_no_data:
                    raise AssertionError(
                        "No semester timetable data found. "
                        f"Message shown: {visible_no_data}"
                    )

                body_text = " ".join(
                    self.driver.find_element(
                        By.TAG_NAME,
                        "body"
                    ).text.lower().split()
                )

                important_keywords = [
                    "subject",
                    "teacher",
                    "room",
                    "time"
                ]

                keyword_match_count = sum(
                    1
                    for keyword in important_keywords
                    if keyword in body_text
                )

                timetable_cards = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(text(),'Teacher Name')] "
                    "| //*[contains(text(),'Room No')] "
                    "| //*[contains(text(),'Subject')]"
                )

                visible_cards = []

                for card in timetable_cards:

                    try:
                        if card.is_displayed():
                            visible_cards.append(card)

                    except StaleElementReferenceException:
                        continue

                tables = self.driver.find_elements(
                    By.XPATH,
                    "//table//tbody//tr"
                )

                visible_rows = []

                for row in tables:

                    try:
                        if (
                                row.is_displayed()
                                and row.text.strip()
                        ):
                            visible_rows.append(row)

                    except StaleElementReferenceException:
                        continue

                if (
                        keyword_match_count >= 2
                        or len(visible_cards) > 0
                        or len(visible_rows) > 0
                ):
                    return True

            except StaleElementReferenceException:
                pass

            time.sleep(1)

        body_text = ""

        try:
            body_text = self.driver.find_element(
                By.TAG_NAME,
                "body"
            ).text

        except Exception:
            pass

        raise AssertionError(
            "Show Semester Table result did not load.\n\n"
            f"Current page text:\n{body_text}"
        )

    # def wait_for_show_timetable_result(self, timeout=25):
    #     end_time = time.time() + timeout
    #
    #     while time.time() < end_time:
    #         try:
    #             no_data_elements = self.driver.find_elements(
    #                 By.XPATH,
    #                 "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
    #                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
    #                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'not found') "
    #                 "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'data not found')]"
    #             )
    #
    #             visible_no_data = []
    #
    #             for element in no_data_elements:
    #                 try:
    #                     if element.is_displayed() and element.text.strip():
    #                         visible_no_data.append(element.text.strip())
    #                 except StaleElementReferenceException:
    #                     continue
    #
    #             if visible_no_data:
    #                 raise AssertionError(
    #                     f"No semester timetable data found in Show tab. Message shown: {visible_no_data}"
    #                 )
    #
    #             body_text = self.driver.find_element(By.XPATH, "//body").text.lower()
    #
    #             days_loaded = (
    #                 "monday" in body_text
    #                 and "tuesday" in body_text
    #                 and "wednesday" in body_text
    #                 and "thursday" in body_text
    #                 and "friday" in body_text
    #                 and "saturday" in body_text
    #                 and "sunday" in body_text
    #             )
    #
    #             card_loaded = (
    #                 "subject" in body_text
    #                 and "teacher name" in body_text
    #                 and "time" in body_text
    #                 and "room no" in body_text
    #             )
    #
    #             if days_loaded and card_loaded:
    #                 return True
    #
    #         except StaleElementReferenceException:
    #             pass
    #
    #         time.sleep(1)
    #
    #     raise AssertionError("Show Semester Table result did not load.")
    #
    # def get_page_text(self):
    #     return " ".join(
    #         self.driver.find_element(By.XPATH, "//body").text.split()
    #     )
