import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AdmissionReportPage:
    EMAIL = (By.XPATH, "//input[@type='email' or @name='email']")
    PASSWORD = (By.XPATH, "//input[@type='password' or @name='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Login']")

    FROM_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'From Date')]/following::input[1]"
    )

    TO_DATE = (
        By.XPATH,
        "//label[contains(normalize-space(),'To Date')]/following::input[1]"
    )

    SEARCH_BUTTON = (
        By.XPATH,
        "//button[@class='btn btn-primary btn-icon']"
    )

    DATA_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Data'] | //a[normalize-space()='Data']"
    )

    GRAPH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Graph'] | //a[normalize-space()='Graph']"
    )

    DOWNLOAD_BUTTON = (
        By.XPATH,
        "//*[local-name()='svg' or self::i or self::button or self::mat-icon][contains(@class,'download') or contains(@class,'cloud') or contains(@class,'fa-download')]"
    )

    PRINT_BUTTON = (
        By.XPATH,
        "//*[local-name()='svg' or self::i or self::button or self::mat-icon][contains(@class,'print') or contains(@class,'fa-print')]"
    )

    REPORT_TITLE = (
        By.XPATH,
        "//*[contains(normalize-space(),'STUDENT ADMISSION REPORT')]"
    )

    REPORT_TABLE = (
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
        element.clear()
        element.send_keys(text)
        time.sleep(0.7)

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

    def login(self, email, password):
        self.enter_text(self.EMAIL, email)
        self.enter_text(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def enter_from_date(self, date_value):
        self.enter_date(self.FROM_DATE, date_value)

    def enter_to_date(self, date_value):
        self.enter_date(self.TO_DATE, date_value)

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def click_data(self):
        self.click(self.DATA_BUTTON)

    def click_graph(self):
        self.click(self.GRAPH_BUTTON)

    def click_download(self):
        self.click(self.DOWNLOAD_BUTTON)

    def click_print(self):
        self.click(self.PRINT_BUTTON)

    def wait_for_report_table(self):
        self.wait.until(EC.presence_of_element_located(self.REPORT_TABLE))
        time.sleep(1)

    def get_table_rows(self):
        return self.driver.find_elements(By.XPATH, "//table//tbody//tr")

    def get_report_title_text(self):
        element = self.scroll(self.REPORT_TITLE)
        return element.text.strip()