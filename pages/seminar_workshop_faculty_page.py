import time
from pathlib import Path

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeminarWorkshopFacultyPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_TAB = (
        By.XPATH,
        "//button[normalize-space()='Add']"
        "|//a[normalize-space()='Add']"
    )

    SHOW_TAB = (
        By.XPATH,
        "//button[normalize-space()='Show']"
        "|//a[normalize-space()='Show']"
    )

    STAFF_DROPDOWN = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Staff')]/following::ng-select[1]"
    )

    TITLE = (
        By.XPATH,
        "//input[@placeholder='Title of Seminar/Workshop']"
    )

    TYPE = (
        By.XPATH,
        "//input[@placeholder='Type of Seminar/Workshop']"
    )

    ORGANIZED_BY = (
        By.XPATH,
        "//input[@placeholder='Organized By']"
    )

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    DURATION = (
        By.XPATH,
        "//input[@placeholder='Duration']"
    )

    ACHIEVEMENT = (
        By.XPATH,
        "//input[@placeholder='Achievement']"
    )

    FILE_INPUT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Upload File')]/following::input[@type='file'][1]"
    )

    SHOW_FROM_DATE = (
        By.XPATH,
        "//*[normalize-space()='SHOW ALL']/following::label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    SHOW_TO_DATE = (
        By.XPATH,
        "//*[normalize-space()='SHOW ALL']/following::label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    SHOW_STAFF_DROPDOWN = (
        By.XPATH,
        "//*[normalize-space()='SHOW ALL']/following::label[contains(normalize-space(),'Select Staff')][1]/following::ng-select[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//*[normalize-space()='SHOW ALL']/following::button[normalize-space()='Search'][1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
    )

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

    def select_staff_by_name(self, staff_name, timeout=35):
        end_time = time.time() + timeout
        expected_name = " ".join(staff_name.lower().split())

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.STAFF_DROPDOWN)
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

                staff_options = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                )

                for staff_option in staff_options:
                    try:
                        option_text = " ".join(staff_option.text.split())

                        if (
                            staff_option.is_displayed()
                            and option_text
                            and expected_name in option_text.lower()
                        ):
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
            "\nStaff Selection Failed\n"
            "----------------------\n"
            "Expected Result : Staff should be clicked and selected from Select Staff dropdown.\n"
            "Actual Result   : Staff option was not clicked/selected.\n\n"
            f"Staff Name      : {staff_name}\n\n"
            "Possible Reason :\n"
            "1. Staff name is not available in dropdown.\n"
            "2. Dropdown opened but option was not visible/clickable.\n"
            "3. Page loader or overlay blocked the dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def select_show_staff_by_name(self, staff_name, timeout=35):
        end_time = time.time() + timeout
        expected_name = " ".join(staff_name.lower().split())

        while time.time() < end_time:
            try:
                ng_select = self.wait.until(
                    EC.presence_of_element_located(self.SHOW_STAFF_DROPDOWN)
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    ng_select
                )

                time.sleep(0.5)

                selected_text = " ".join(ng_select.text.split())

                if expected_name in selected_text.lower():
                    return selected_text

                try:
                    ng_select.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();",
                        ng_select
                    )

                time.sleep(1)

                search_input = None

                input_locators = [
                    ".//input[@type='text']",
                    "//div[contains(@class,'ng-select-opened')]//input[@type='text']",
                    "//ng-dropdown-panel/preceding::input[@type='text'][1]"
                ]

                for input_locator in input_locators:
                    try:
                        if input_locator.startswith("."):
                            search_input = ng_select.find_element(
                                By.XPATH,
                                input_locator
                            )
                        else:
                            search_input = self.driver.find_element(
                                By.XPATH,
                                input_locator
                            )

                        if search_input.is_displayed():
                            break

                    except Exception:
                        search_input = None

                assert search_input is not None, (
                    "Search input was not found inside Show Seminar staff dropdown."
                )

                try:
                    search_input.clear()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].value='';",
                        search_input
                    )

                search_input.send_keys(staff_name)

                self.driver.execute_script(
                    """
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('keyup', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                    search_input
                )

                time.sleep(2)

                staff_options = self.driver.find_elements(
                    By.XPATH,
                    "//ng-dropdown-panel//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                )

                if len(staff_options) == 0:
                    staff_options = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(@class,'ng-option') and not(contains(@class,'disabled'))]"
                    )

                for staff_option in staff_options:
                    try:
                        option_text = " ".join(staff_option.text.split())

                        if (
                            staff_option.is_displayed()
                            and option_text
                            and expected_name in option_text.lower()
                        ):
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

                            ng_select = self.wait.until(
                                EC.presence_of_element_located(self.SHOW_STAFF_DROPDOWN)
                            )

                            selected_text = " ".join(ng_select.text.split())

                            assert expected_name in selected_text.lower(), (
                                f"Show staff was clicked but not selected. "
                                f"Expected staff: {staff_name}. "
                                f"Clicked option: {option_text}. "
                                f"Selected text: {selected_text}"
                            )

                            return option_text

                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue

                try:
                    search_input.send_keys(Keys.ENTER)
                    time.sleep(1.5)

                    ng_select = self.wait.until(
                        EC.presence_of_element_located(self.SHOW_STAFF_DROPDOWN)
                    )

                    selected_text = " ".join(ng_select.text.split())

                    if expected_name in selected_text.lower():
                        return selected_text

                except Exception:
                    pass

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
            "\nShow Seminar Staff Selection Failed\n"
            "-----------------------------------\n"
            "Expected Result : Staff should be typed, clicked and selected from Show dropdown.\n"
            "Actual Result   : Staff option was not clicked/selected.\n\n"
            f"Staff Name      : {staff_name}\n\n"
            "Possible Reason :\n"
            "1. Staff name is not available in Show Seminar dropdown.\n"
            "2. Dropdown options are loading only after typing staff name.\n"
            "3. Dropdown option was not visible/clickable.\n"
            "4. Page loader or overlay blocked the dropdown.\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def enter_title(self, value):
        self.enter_text(self.TITLE, value)

    def enter_type(self, value):
        self.enter_text(self.TYPE, value)

    def enter_organized_by(self, value):
        self.enter_text(self.ORGANIZED_BY, value)

    def enter_from_date(self, value):
        self.enter_date(self.FROM_DATE, value)

    def enter_to_date(self, value):
        self.enter_date(self.TO_DATE, value)

    def enter_duration(self, value):
        self.enter_text(self.DURATION, value)

    def enter_achievement(self, value):
        self.enter_text(self.ACHIEVEMENT, value)

    def enter_show_from_date(self, value):
        self.enter_date(self.SHOW_FROM_DATE, value)

    def enter_show_to_date(self, value):
        self.enter_date(self.SHOW_TO_DATE, value)

    def upload_file(self, file_path):
        file_path = str(Path(file_path).resolve())

        file_input = self.wait.until(
            EC.presence_of_element_located(self.FILE_INPUT)
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            file_input
        )

        assert Path(file_path).exists(), (
            f"Seminar upload file path does not exist: {file_path}"
        )

        file_input.send_keys(file_path)

        time.sleep(2)
        return True

    def click_add_tab(self):
        self.click_visible_element(
            self.ADD_TAB,
            element_name="Add Tab",
            timeout=35
        )

    def click_show_tab(self):
        self.click_visible_element(
            self.SHOW_TAB,
            element_name="Show Tab",
            timeout=35
        )

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def search_seminar(self, from_date, to_date, staff_name):
        self.enter_show_from_date(from_date)
        self.enter_show_to_date(to_date)
        self.select_show_staff_by_name(staff_name)
        self.click_search()

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
                break

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
            f"Download link/icon was not found for exact seminar row. "
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
                break

        if matching_row:
            self.driver.execute_script(
                """
                let containers = document.querySelectorAll(
                    '.table-responsive, .dataTables_scrollBody, .mat-table, table'
                );

                containers.forEach(function(container) {
                    container.scrollLeft = container.scrollWidth;
                });
                """
            )

            time.sleep(0.8)

            action_cell = matching_row.find_element(By.XPATH, ".//td[last()]")

            edit_button = action_cell.find_element(
                By.XPATH,
                ".//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'pencil') "
                "or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') "
                "or self::button or self::a or self::i or self::mat-icon or local-name()='svg'][1]"
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center', inline:'end'});",
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
            f"Edit button was not found for exact seminar row. "
            f"Expected values: {expected_values}. "
            f"Actual table text: {table_text}"
        )

    def click_delete_for_exact_row(self, expected_values):
        expected_values = [
            str(value).lower().strip()
            for value in expected_values
        ]

        end_time = time.time() + 35

        while time.time() < end_time:
            try:
                rows = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

                for row in rows:
                    row_text = " ".join(row.text.lower().split())

                    if all(value in row_text for value in expected_values):
                        self.driver.execute_script(
                            """
                            let containers = document.querySelectorAll(
                                '.table-responsive, .dataTables_scrollBody, .mat-table, table'
                            );

                            containers.forEach(function(container) {
                                container.scrollLeft = container.scrollWidth;
                            });
                            """
                        )

                        time.sleep(1)

                        action_cell = row.find_element(By.XPATH, ".//td[last()]")

                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center', inline:'end'});",
                            action_cell
                        )

                        time.sleep(0.8)

                        delete_icons = action_cell.find_elements(
                            By.XPATH,
                            ".//*[contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'trash') "
                            "or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') "
                            "or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') "
                            "or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete') "
                            "or contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'delete')]"
                        )

                        for delete_icon in delete_icons:
                            try:
                                if delete_icon.is_displayed():
                                    delete_button = self.driver.execute_script(
                                        """
                                        let element = arguments[0];

                                        while (element) {
                                            if (
                                                element.tagName &&
                                                (
                                                    element.tagName.toLowerCase() === 'button' ||
                                                    element.tagName.toLowerCase() === 'a'
                                                )
                                            ) {
                                                return element;
                                            }

                                            element = element.parentElement;
                                        }

                                        return arguments[0];
                                        """,
                                        delete_icon
                                    )

                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block:'center', inline:'end'});",
                                        delete_button
                                    )

                                    time.sleep(0.8)

                                    try:
                                        delete_button.click()
                                    except Exception:
                                        self.driver.execute_script(
                                            "arguments[0].click();",
                                            delete_button
                                        )

                                    time.sleep(1.5)
                                    return True

                            except StaleElementReferenceException:
                                continue
                            except Exception:
                                continue

                        clickable_items = action_cell.find_elements(
                            By.XPATH,
                            ".//*[self::button or self::a]"
                        )

                        if len(clickable_items) > 0:
                            delete_button = clickable_items[-1]

                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center', inline:'end'});",
                                delete_button
                            )

                            time.sleep(0.8)

                            try:
                                delete_button.click()
                            except Exception:
                                self.driver.execute_script(
                                    "arguments[0].click();",
                                    delete_button
                                )

                            time.sleep(1.5)
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
            table_text = self.driver.find_element(By.XPATH, "//body").text

        raise AssertionError(
            f"Delete button was not clicked for exact seminar row. "
            f"Expected values: {expected_values}. "
            f"Actual table/page text: {table_text}"
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

    def confirm_update_if_present(self):
        confirm_xpaths = [
            "//button[normalize-space()='Yes, save it!']",
            "//button[normalize-space()='Yes, Save It!']",
            "//button[normalize-space()='Yes, update it!']",
            "//button[normalize-space()='Yes, Update It!']",
            "//button[normalize-space()='Yes']",
            "//button[contains(normalize-space(),'save')]",
            "//button[contains(normalize-space(),'Save')]",
            "//button[contains(normalize-space(),'update')]",
            "//button[contains(normalize-space(),'Update')]",
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