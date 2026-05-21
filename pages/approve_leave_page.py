import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ApproveLeavePage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    PENDING_LEAVE_TAB = (
        By.XPATH,
        "(//a[normalize-space()='Pending Leave'])[1]"
    )

    APPROVED_LEAVE_TAB = (
        By.XPATH,
        "(//a[normalize-space()='Approved Leave'])[1]"
    )

    NON_APPROVED_LEAVE_TAB = (
        By.XPATH,
        "(//a[normalize-space()='Non Approved Leave'])[1]"
    )

    SEARCH_INPUT = (
        By.XPATH,
        "//input[@placeholder='Search Or Filter']"
    )

    TABLE_ROWS = (
        By.XPATH,
        "//table//tbody//tr"
    )

    APPROVE_BUTTON = (
        By.XPATH,
        "(//table//tbody//tr[1]//td[last()]//*[local-name()='svg' or self::i or self::button or self::mat-icon])[1]"
    )

    REJECT_BUTTON = (
        By.XPATH,
        "(//button[@class='btn btn-primary me-1'][normalize-space()='Reject'])[1]"
    )

    YES_ACCEPT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'Accept')]"
    )


    YES_REJECT_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'Yes') and contains(normalize-space(),'Reject')]"
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

    def click_pending_leave_tab(self):
        self.click(self.PENDING_LEAVE_TAB)

    def click_approved_leave_tab(self):
        self.click(self.APPROVED_LEAVE_TAB)

    def click_non_approved_leave_tab(self):
        self.click(self.NON_APPROVED_LEAVE_TAB)

    def search_leave(self, keyword):
        self.enter_text(self.SEARCH_INPUT, keyword)

    def click_approve(self):
        self.scroll_table_to_right()
        self.click(self.APPROVE_BUTTON)

    def click_reject(self):
        self.scroll_table_to_right()
        self.click(self.REJECT_BUTTON)

    def confirm_approve(self):
        self.click(self.YES_ACCEPT_BUTTON)

    def confirm_reject(self):
        self.click(self.YES_REJECT_BUTTON)