import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class StaffEducationPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_STAFF_EDUCATION_TAB = (
        By.XPATH,
        "//button[normalize-space()='Add Staff Education']"
        "|//a[normalize-space()='Add Staff Education']"
    )

    SHOW_STAFF_EDUCATION_TAB = (
        By.XPATH,
        "//button[normalize-space()='Show Staff Education']"
        "|//a[normalize-space()='Show Staff Education']"
    )

    STAFF_NG_SELECT = (
        By.XPATH,
        "//label[normalize-space()='Select Staff']/following::ng-select[1]"
    )

    DEGREE = (
        By.XPATH,
        "//label[normalize-space()='Select Degree']/following::select[1]"
    )

    SPECIALIZATION = (
        By.XPATH,
        "//input[@placeholder='specialization']"
    )

    UNIVERSITY_NAME = (
        By.XPATH,
        "//input[@placeholder='university_name']"
    )

    PERCENTAGE = (
        By.XPATH,
        "//input[@placeholder='percentage']"
    )

    GRADE = (
        By.XPATH,
        "//input[@placeholder='grade']"
    )

    FILE_INPUT = (
        By.XPATH,
        "//label[normalize-space()='File']/following::input[@type='file'][1]"
    )

    SHOW_STAFF_NG_SELECT = (
        By.XPATH,
        "//label[normalize-space()='Select Staff']/following::ng-select[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search']"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
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

    def select_staff_by_text(self, staff_name):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.STAFF_NG_SELECT)
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

                time.sleep(1)

                staff_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f"//*[normalize-space()='{staff_name}']"
                        )
                    )
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    staff_option
                )

                try:
                    staff_option.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        staff_option
                    )

                time.sleep(1.5)

                page_text = " ".join(
                    self.driver.find_element(By.XPATH, "//body").text.split()
                )

                assert staff_name in page_text, (
                    f"Staff was clicked but not selected. "
                    f"Expected staff: {staff_name}. "
                    f"Actual page text: {page_text}"
                )

                return staff_name

            except StaleElementReferenceException:
                time.sleep(1)
            except Exception:
                time.sleep(1)

        raise AssertionError(
            f"Staff option '{staff_name}' was not clicked/selected after waiting 30 seconds."
        )

    def select_show_staff_by_text(self, staff_name):
        end_time = time.time() + 30

        while time.time() < end_time:
            try:
                ng_selects = self.driver.find_elements(*self.SHOW_STAFF_NG_SELECT)

                visible_ng_select = None

                for ng_select in ng_selects:
                    try:
                        if ng_select.is_displayed():
                            visible_ng_select = ng_select
                            break
                    except Exception:
                        continue

                if visible_ng_select is None:
                    visible_ng_select = self.wait.until(
                        EC.presence_of_element_located(self.SHOW_STAFF_NG_SELECT)
                    )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    visible_ng_select
                )

                try:
                    visible_ng_select.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        visible_ng_select
                    )

                time.sleep(1)

                try:
                    input_box = visible_ng_select.find_element(By.XPATH, ".//input")
                    input_box.send_keys(staff_name)
                    time.sleep(1)
                except Exception:
                    pass

                staff_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f"//ng-dropdown-panel//*[normalize-space()='{staff_name}']"
                            f"|//*[normalize-space()='{staff_name}']"
                        )
                    )
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    staff_option
                )

                try:
                    staff_option.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        staff_option
                    )

                time.sleep(1.5)

                page_text = " ".join(
                    self.driver.find_element(By.XPATH, "//body").text.split()
                )

                assert staff_name in page_text, (
                    f"Show Staff was clicked but not selected. "
                    f"Expected staff: {staff_name}. "
                    f"Actual page text: {page_text}"
                )

                return staff_name

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
            "\nSearch Staff Selection Failed\n"
            "-----------------------------\n"
            "Expected Result : Staff should be selectable in Show Staff Education search field.\n"
            "Actual Result   : Staff dropdown/input was not interactable or staff option was not selected.\n\n"
            f"Staff Name      : {staff_name}\n\n"
            "Possible Reason :\n"
            "1. Wrong hidden input was selected by locator.\n"
            "2. Show Staff Education tab did not load properly.\n"
            "3. Staff dropdown option was not visible.\n"
            "4. Page loader or overlay blocked the staff dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def select_staff_shyam_samanta(self):
        return self.select_staff_by_text("Shyam Samanta")

    def select_degree_msc(self):
        return self.select_by_visible_text(
            self.DEGREE,
            "Msc",
            "degree"
        )

    def enter_specialization(self, value):
        self.enter_text(self.SPECIALIZATION, value)

    def enter_university_name(self, value):
        self.enter_text(self.UNIVERSITY_NAME, value)

    def enter_percentage(self, value):
        self.enter_text(self.PERCENTAGE, value)

    def enter_grade(self, value):
        self.enter_text(self.GRADE, value)

    def upload_file(self, file_path):
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
            f"Staff education file path does not exist: {file_path}"
        )

        return True

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_show_staff_education(self):
        self.click(self.SHOW_STAFF_EDUCATION_TAB)

    def click_add_staff_education(self):
        self.click(self.ADD_STAFF_EDUCATION_TAB)

    def search_staff_education(self, staff_name):
        self.select_show_staff_by_text(staff_name)
        self.click(self.SEARCH_BUTTON)

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
                "or self::button or self::i or self::mat-icon or local-name()='svg'][1]"
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
                "Download icon was clicked, but browser window state became invalid."
            )

            return True

        table_text = self.driver.find_element(By.XPATH, "//table//tbody").text

        raise AssertionError(
            f"Download icon was not found for exact staff education row. "
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
            f"Edit button was not found for exact staff education row. "
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
            f"Delete button was not found for exact staff education row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def confirm_delete_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Save It!']",
            "//button[normalize-space()='Yes, delete it!']",
            "//button[normalize-space()='Yes, Delete It!']",
            "//button[normalize-space()='Yes, delete!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'Yes')]",
            "//button[contains(normalize-space(),'save')]",
            "//button[contains(normalize-space(),'Save')]",
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
            "Expected button like 'Yes, save it!' or 'Yes, delete it!' but no matching clickable button was found.\n"
            f"Actual page text:\n{modal_text}"
        )

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)