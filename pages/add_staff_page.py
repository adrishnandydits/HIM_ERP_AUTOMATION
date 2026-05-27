import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class AddStaffPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    ADD_STAFF_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Add Staff']"
    )

    SHOW_STAFF_BUTTON = (
        By.XPATH,
        "(//a[normalize-space()='Show Staff'])[1]"
    )

    FILL_FORM = (By.XPATH, "//div[contains(text(),'Fill Form')]")

    BANK_ACCOUNT_DETAILS = (By.XPATH, "//div[contains(text(),'Bank Account Details')]")

    STAFF_ID = (
        By.XPATH,
        "//input[@placeholder='Staff Id']"
    )

    FIRST_NAME = (
        By.XPATH,
        "//input[@placeholder='First name']"
    )

    MIDDLE_NAME = (
        By.XPATH,
        "//input[@placeholder='Middle Name']"
    )

    LAST_NAME = (
        By.XPATH,
        "//input[@placeholder='Last Name']"
    )

    GENDER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Gender')]/following::select[1]"
    )

    DATE_OF_BIRTH = (
        By.XPATH,
        "//label[contains(normalize-space(),'Date Of Birth')]/following::input[1]"
    )

    DATE_OF_JOINING = (
        By.XPATH,
        "//label[contains(normalize-space(),'Date Of Joining')]/following::input[1]"
    )

    PHONE_NUMBER = (
        By.XPATH,
        "//input[@placeholder='Phone Number']"
    )

    EMERGENCY_CONTACT_NUMBER = (
        By.XPATH,
        "//input[@placeholder='Emergency Contact Number']"
    )

    MATERIAL_STATUS = (
        By.XPATH,
        "//label[contains(normalize-space(),'Material Status')]/following::select[1]"
    )

    WORK_EXPERIENCE = (
        By.XPATH,
        "//input[@placeholder='Work Experience']"
    )

    QUALIFICATION = (
        By.XPATH,
        "//input[@placeholder='Qualification']"
    )

    BLOOD_GROUP = (
        By.XPATH,
        "//label[contains(normalize-space(),'Blood Group')]/following::select[1]"
    )

    RELIGION = (
        By.XPATH,
        "//label[contains(normalize-space(),'Religion')]/following::select[1]"
    )

    USER_TYPE = (
        By.XPATH,
        "//label[contains(normalize-space(),'User Type')]/following::select[1]"
    )

    EMAIL_ADDRESS = (
        By.XPATH,
        "//input[@placeholder='name@example.com']"
    )

    CASTE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Caste')]/following::select[1]"
    )

    DEPARTMENT = (
        By.XPATH,
        "//label[contains(normalize-space(),'Department')]/following::select[1]"
    )

    FRANCHISE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Select Franchise')]/following::select[1]"
    )

    DESIGNATION = (
        By.XPATH,
        "//label[contains(normalize-space(),'Designation')]/following::select[1]"
    )

    CURRENT_ADDRESS = (
        By.XPATH,
        "//input[@placeholder='Current Address']"
    )

    PERMANENT_ADDRESS = (
        By.XPATH,
        "//input[@placeholder='Permanent Address']"
    )

    PAN_NUMBER = (
        By.XPATH,
        "//input[@placeholder='Enter Pan Number']"
    )

    NEXT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Next']"
    )

    BACK_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Back']"
    )

    FILE_INPUT = (
        By.XPATH,
        "//input[@type='file']"
    )

    EPF_NUMBER = (
        By.XPATH,
        "//label[contains(normalize-space(),'EPF Number')]/following::input[1]"
    )

    GROSS_SALARY = (
        By.XPATH,
        "//label[contains(normalize-space(),'Gross Salary')]/following::input[1]"
    )

    LOCATION = (
        By.XPATH,
        "//label[contains(normalize-space(),'Location')]/following::input[1]"
    )

    CONTRACT_TYPE = (
        By.XPATH,
        "//label[contains(normalize-space(),'Contract Type')]/following::select[1]"
    )

    BANK_ACCOUNT_NUMBER = (
        By.XPATH,
        "//label[contains(normalize-space(),'Bank Account Number')]/following::input[1]"
    )

    BANK_NAME = (
        By.XPATH,
        "//label[contains(normalize-space(),'Bank Name')]/following::input[1]"
    )

    IFSC_CODE = (
        By.XPATH,
        "//label[contains(normalize-space(),'IFSC Code')]/following::input[1]"
    )

    BANK_BRANCH_NAME = (
        By.XPATH,
        "//label[contains(normalize-space(),'Bank Branch name')]/following::input[1]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Submit']"
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
        "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'delete')]"
    )

    UPDATE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Update']"
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

    def upload_document(self, file_path):
        file_path = str(Path(file_path).resolve())

        file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")

        if len(file_inputs) == 0:
            raise Exception("No file input found on the page")

        for i in range(len(file_inputs)):
            file_inputs[i].send_keys(file_path)
            time.sleep(0.5)

        time.sleep(2)

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

    def click_add_staff(self):
        self.click(self.ADD_STAFF_BUTTON)

    def click_show_staff(self):
        self.click(self.SHOW_STAFF_BUTTON)

    def enter_staff_id(self, staff_id):
        self.enter_text(self.STAFF_ID, staff_id)

    def enter_first_name(self, first_name):
        self.enter_text(self.FIRST_NAME, first_name)

    def enter_middle_name(self, middle_name):
        self.enter_text(self.MIDDLE_NAME, middle_name)

    def enter_last_name(self, last_name):
        self.enter_text(self.LAST_NAME, last_name)

    def select_gender(self):
        self.select_by_visible_text(self.GENDER, "Male")

    def enter_date_of_birth(self, date_value):
        self.enter_date(self.DATE_OF_BIRTH, date_value)

    def enter_date_of_joining(self, date_value):
        self.enter_date(self.DATE_OF_JOINING, date_value)

    def enter_phone_number(self, phone):
        self.enter_text(self.PHONE_NUMBER, phone)

    def enter_emergency_contact_number(self, phone):
        self.enter_text(self.EMERGENCY_CONTACT_NUMBER, phone)

    def select_material_status(self):
        self.select_by_visible_text(self.MATERIAL_STATUS, "Single")

    def enter_work_experience(self, experience):
        self.enter_text(self.WORK_EXPERIENCE, experience)

    def enter_qualification(self, qualification):
        self.enter_text(self.QUALIFICATION, qualification)

    def select_blood_group(self):
        self.select_by_visible_text(self.BLOOD_GROUP, "A+")

    def select_religion(self):
        self.select_by_visible_text(self.RELIGION, "Hinduism")

    def select_user_type(self):
        self.select_by_visible_text(self.USER_TYPE, "Teacher")

    def enter_email_address(self, email):
        self.enter_text(self.EMAIL_ADDRESS, email)

    def select_caste(self):
        self.select_by_visible_text(self.CASTE, "General")

    def select_department(self):
        self.select_by_visible_text(self.DEPARTMENT, "Accounts")

    def select_franchise(self):
        self.select_by_visible_text(self.FRANCHISE, "test")

    def select_designation(self):
        self.select_by_visible_text(self.DESIGNATION, "ACCOUNTANT")

    def enter_current_address(self, address):
        self.enter_text(self.CURRENT_ADDRESS, address)

    def enter_permanent_address(self, address):
        self.enter_text(self.PERMANENT_ADDRESS, address)

    def enter_pan_number(self, pan_number):
        self.enter_text(self.PAN_NUMBER, pan_number)

    def click_fill_form(self):
        self.click(self.FILL_FORM)

    def click_bank_account_details(self):
        self.click(self.BANK_ACCOUNT_DETAILS)

    def click_next(self):
        self.click(self.NEXT_BUTTON)

    def upload_staff_documents(self, file_path):
        self.upload_document(file_path)

    def enter_epf_number(self, epf_number):
        self.enter_text(self.EPF_NUMBER, epf_number)

    def enter_gross_salary(self, salary):
        self.enter_text(self.GROSS_SALARY, salary)

    def enter_location(self, location):
        self.enter_text(self.LOCATION, location)

    def select_contract_type(self):
        self.select_by_visible_text(self.CONTRACT_TYPE, "Permanent")

    def enter_bank_account_number(self, account_number):
        self.enter_text(self.BANK_ACCOUNT_NUMBER, account_number)

    def enter_bank_name(self, bank_name):
        self.enter_text(self.BANK_NAME, bank_name)

    def enter_ifsc_code(self, ifsc_code):
        self.enter_text(self.IFSC_CODE, ifsc_code)

    def enter_bank_branch_name(self, branch_name):
        self.enter_text(self.BANK_BRANCH_NAME, branch_name)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_edit(self):
        self.scroll_table_to_right()
        self.click(self.EDIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_delete(self):
        self.scroll_table_to_right()
        self.click(self.DELETE_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)