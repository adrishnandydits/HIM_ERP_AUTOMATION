from pages.book_list_page import BookListPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
BOOK_LIST_URL = "https://devanttest.in/him_test/#/library/book-list"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

SEARCH_BOOK_NAME = "Test Book 7412"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
    )

    visible_errors = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_book_list_table(driver, timeout=30):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
            return True

        time.sleep(1)

    page_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "Book List table was not loaded. "
        f"Actual page text: {page_text}"
    )


def verify_book_list_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "book list" in page_text, (
        "Book List page heading was not found."
    )

    assert "books list" in page_text, (
        "Books List section heading was not found."
    )

    assert "search" in page_text, (
        "Search section was not found on Book List page."
    )

    assert "book name" in page_text, (
        "Book Name table column was not found."
    )

    assert "author name" in page_text, (
        "Author Name table column was not found."
    )

    assert "publisher name" in page_text, (
        "Publisher Name table column was not found."
    )

    assert "rack no" in page_text, (
        "Rack No table column was not found."
    )

    assert "book price" in page_text, (
        "Book Price table column was not found."
    )

    assert "sbin no" in page_text or "isbn no" in page_text, (
        "SBIN/ISBN No table column was not found."
    )

    return True


def test_book_list_search_download_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = BookListPage(driver)

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

        driver.get(BOOK_LIST_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "book-list" in driver.current_url.lower(), (
            f"Book List page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Book List Page")

        verify_book_list_page(driver)
        wait_for_book_list_table(driver, timeout=30)
        page.verify_books_table_loaded()
        add_step(steps, driver, "Verify Book List Table Loaded")

        page.search_book(SEARCH_BOOK_NAME)
        add_step(steps, driver, "Search Book")

        page.verify_search_result(SEARCH_BOOK_NAME)
        add_step(steps, driver, "Verify Book Search Result")

        page.click_download_button()
        add_step(steps, driver, "Click Book List Download Button")

        verify_no_validation_error(driver)

    except Exception as e:
        error_reason = str(e).strip()

        if not error_reason:
            error_reason = "No detailed error message returned by Selenium."

        error_reason = f"{type(e).__name__}: {error_reason}"

        try:
            add_step(
                steps,
                driver,
                "Test Failed",
                "FAIL",
                reason=error_reason
            )
        except Exception:
            steps.append({
                "name": "Test Failed",
                "status": "FAIL",
                "reason": error_reason,
                "image": ""
            })

        raise e

    finally:
        create_pdf_report("Book_List_Test_Report", steps)