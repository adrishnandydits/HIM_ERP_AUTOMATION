import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class SponsoredOrConsultancyPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_SPONSORED_PROJECT_CONSULTANCY_TAB = (
        By.XPATH,
        "//button[normalize-space()='Add Sponsored Project/Consultancy']"
        "|//a[normalize-space()='Add Sponsored Project/Consultancy']"
    )

    SHOW_SPONSORED_PROJECT_CONSULTANCY_TAB = (
        By.XPATH,
        "//button[normalize-space()='Show Sponsored Project/Consultancy']"
        "|//a[normalize-space()='Show Sponsored Project/Consultancy']"
    )

    STAFF_DROPDOWN = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Staff')]/following::ng-select[1]"
    )

    PROJECT_CONSULTANCY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Project/Consultancy')]/following::input[1]"
    )

    SPONSORED_BY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Sponsored By')]/following::input[1]"
    )

    CONSULTANT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Consultant')]/following::input[1]"
    )

    AMOUNT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Amount')]/following::input[1]"
    )

    DURATION = (
        By.XPATH,
        "//label[contains(normalize-space(),'Duration')]/following::input[1]"
    )

    STATUS = (
        By.XPATH,
        "//label[contains(normalize-space(),'Status')]/following::select[1]"
    )

    SHOW_STAFF_DROPDOWN = (
        By.XPATH,
        "//*[normalize-space()='SHOW SPONSORED PROJECT/CONSULTANCY']/following::button[normalize-space()='Search']/preceding::ng-select[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//*[normalize-space()='SHOW SPONSORED PROJECT/CONSULTANCY']/following::button[normalize-space()='Search'][1]"
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
            "\nShow Sponsored Project/Consultancy Staff Selection Failed\n"
            "---------------------------------------------------------\n"
            "Expected Result : Staff should be clicked and selected from Show dropdown.\n"
            "Actual Result   : Staff option was not clicked/selected.\n\n"
            f"Staff Name      : {staff_name}\n\n"
            f"Actual Page Text:\n{page_text}"
        )

    def enter_project_consultancy(self, value):
        self.enter_text(self.PROJECT_CONSULTANCY, value)

    def enter_sponsored_by(self, value):
        self.enter_text(self.SPONSORED_BY, value)

    def enter_consultant(self, value):
        self.enter_text(self.CONSULTANT, value)

    def enter_amount(self, value):
        self.enter_text(self.AMOUNT, value)

    def enter_duration(self, value):
        self.enter_text(self.DURATION, value)

    def select_status_ongoing(self):
        return self.select_by_visible_text(
            self.STATUS,
            "Ongoing",
            field_name="status",
            timeout=35
        )

    def click_add_sponsored_project_consultancy(self):
        self.click_visible_element(
            self.ADD_SPONSORED_PROJECT_CONSULTANCY_TAB,
            element_name="Add Sponsored Project Consultancy",
            timeout=35
        )

    def click_show_sponsored_project_consultancy(self):
        self.click_visible_element(
            self.SHOW_SPONSORED_PROJECT_CONSULTANCY_TAB,
            element_name="Show Sponsored Project Consultancy",
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

    def search_sponsored_project_consultancy(self, staff_name):
        self.select_show_staff_by_name(staff_name)
        self.click_search()

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
            f"Edit button was not found for exact sponsored project consultancy row. "
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
            f"Delete button was not clicked for exact sponsored project consultancy row. "
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