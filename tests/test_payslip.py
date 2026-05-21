from pages.payslip_page import PayslipPage

import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
PAYSLIP_URL = "https://devanttest.in/him_test/#/human-resource/payslip"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

MONTH = "January"
YEAR = "2023"

STAFF_NAME = "Priyanka Adak"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS"):
    steps.append({
        "name": name,
        "status": status,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required')]"
    )

    visible_errors = [
        error.text for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def verify_staff_list_loaded(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    assert len(rows) > 0, "No payslip staff list found. Table body is empty."

    return True


def verify_exact_table_row_added(driver, expected_values):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    assert len(rows) > 0, "No payslip staff record found. Table body is empty."

    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    for row in rows:
        row_text = " ".join(row.text.lower().split())

        if all(value in row_text for value in expected_values):
            return True

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact payslip staff row not found. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def test_payslip_search_staff_list_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = PayslipPage(driver)

        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Login Page")

        page.enter_text(page.EMAIL, EMAIL)
        add_step(steps, driver, "Enter Email")

        page.enter_text(page.PASSWORD, PASSWORD)
        add_step(steps, driver, "Enter Password")

        page.click(page.LOGIN_BUTTON)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Login Button")

        driver.get(PAYSLIP_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "payslip" in driver.current_url.lower()

        add_step(steps, driver, "Open Payslip Page")

        page.select_month()
        add_step(steps, driver, "Select Month")

        page.select_year()
        add_step(steps, driver, "Select Year")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        verify_staff_list_loaded(driver)
        add_step(steps, driver, "Verify Staff List Loaded")

        verify_exact_table_row_added(
            driver,
            [STAFF_NAME]
        )
        add_step(steps, driver, "Verify Staff Name In Payslip List")

        page.search_staff(STAFF_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody//tr")))
        add_step(steps, driver, "Search Staff Name")

        verify_exact_table_row_added(
            driver,
            [STAFF_NAME]
        )
        add_step(steps, driver, "Verify Searched Staff Name")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Payslip_Test_Report", steps)