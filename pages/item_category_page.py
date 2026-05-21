import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ItemCategoryPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    NAME = (By.XPATH, "//input[@placeholder='Name' or @placeholder='Enter Name']")
    SUBMIT_BUTTON = (By.XPATH, "//button[normalize-space()='Submit']")
    UPDATE_BUTTON = (By.XPATH, "//button[normalize-space()='Update']")
    CANCEL_BUTTON = (By.XPATH, "//button[normalize-space()='Cancel']")

    EDIT_BUTTON = (
        By.XPATH,
        "(//mat-icon[@role='img'][normalize-space()='edit'])[1]"
    )

    DELETE_BUTTON = (
        By.XPATH,
        "(//mat-icon[@role='img'][normalize-space()='delete'])[1]"
    )

    YES_DELETE_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Yes, delete It!']"
    )

    BODY = (By.XPATH, "//body")

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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def enter_name(self, name):
        self.enter_text(self.NAME, name)

    def click_submit(self):
        self.click(self.SUBMIT_BUTTON)

    def click_edit(self):
        self.click(self.EDIT_BUTTON)

    def click_update(self):
        self.click(self.UPDATE_BUTTON)

    def click_delete(self):
        self.click(self.DELETE_BUTTON)

    def confirm_delete(self):
        self.click(self.YES_DELETE_BUTTON)